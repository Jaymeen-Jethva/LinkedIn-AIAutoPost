"""
LinkedIn Post Generation Workflow

Orchestrates the process of:
1. Generating content with Gemini
2. Generating images (optional)
3. Review loop (Human-in-the-loop)
4. Posting to LinkedIn (via DB credentials)
"""
import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
from typing import TypedDict
from langgraph.graph.state import CompiledStateGraph
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.ai.gemini_client import generate_linkedin_post, generate_linkedin_post_with_search, revise_linkedin_post, generate_image_with_gemini, generate_image_with_pollinations, LinkedInPost
from src.services.linkedin.api_client import linkedin_api
from src.tools.tavily_tool import tavily_search
from src.services.user_service import UserService


@dataclass
class WorkflowState:
    """State maintained throughout the workflow execution"""
    topic: str
    post_type: str = "ai_news"  # ai_news, personal_milestone
    generated_post: Optional[LinkedInPost] = None
    image_path: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    include_image: bool = True
    revision_count: int = 0
    max_revisions: int = 3
    is_approved: bool = False
    feedback: str = ""
    error: Optional[str] = None
    posted_to_linkedin: bool = False
    
    # New fields for DB integration
    user_id: Optional[str] = None
    db_session: Optional[Any] = None  # Valid only during execution scope


class LinkedInWorkflow:
    def __init__(self, use_multi_agent: bool = False):
        self.workflow = self._build_workflow()
        self.use_multi_agent = use_multi_agent
        self.multi_agent_workflow = None
        
        # Initialize multi-agent workflow if requested
        if use_multi_agent:
            try:
                from src.services.ai.agent_orchestrator import MultiAgentGeminiWorkflow
                self.multi_agent_workflow = MultiAgentGeminiWorkflow()
                print("✅ Multi-agent workflow initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to init multi-agent workflow: {e}")
                self.use_multi_agent = False

    def _build_workflow(self) -> CompiledStateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("generate_content", self._generate_content)
        workflow.add_node("generate_image", self._generate_image)
        workflow.add_node("human_review", self._human_review)
        workflow.add_node("revise_content", self._revise_content)
        workflow.add_node("post_to_linkedin", self._post_to_linkedin)

        # Define edges
        workflow.set_entry_point("generate_content")
        
        workflow.add_edge("generate_content", "generate_image")
        workflow.add_edge("generate_image", "human_review")
        
        # Conditional logic after review
        workflow.add_conditional_edges(
            "human_review",
            self._check_review_outcome,
            {
                "approved": "post_to_linkedin",
                "revise": "revise_content",
                "rejected": END
            }
        )
        
        workflow.add_edge("revise_content", "human_review")
        workflow.add_edge("post_to_linkedin", END)

        return workflow.compile()

    def _generate_content(self, state: WorkflowState) -> WorkflowState:
        """Generate initial LinkedIn post content"""
        print(f"🚀 Generating content for topic: {state.topic}")
        
        try:
            # Check if using multi-agent system
            if self.use_multi_agent and self.multi_agent_workflow:
                print("🤖 Delegating to Multi-Agent System...")
                result = self.multi_agent_workflow.generate_post(
                    topic=state.topic,
                    post_type=state.post_type,
                    user_preferences=state.user_preferences,
                    include_image=state.include_image
                )
                
                # Convert dict result to LinkedInPost object
                post = LinkedInPost(
                    content=result.get("content", ""),
                    hashtags=result.get("hashtags", []),
                    image_prompt=result.get("image_prompt", ""),
                    post_type=result.get("post_type", state.post_type)  # Use state fallback
                )
                state.generated_post = post
            else:
                # Use standard single-shot generation (with search if needed)
                if state.post_type == "ai_news":
                    # generate_linkedin_post_with_search returns (post, search_results)
                    post, _ = generate_linkedin_post_with_search(state.topic, state.post_type, state.user_preferences)
                    state.generated_post = post
                else:
                    state.generated_post = generate_linkedin_post(state.topic, state.post_type, state.user_preferences)
            
        except Exception as e:
            state.error = f"Content generation failed: {str(e)}"
            return state
            
        return state

    def _generate_image(self, state: WorkflowState) -> WorkflowState:
        """Generate image if requested"""
        if not state.generated_post or not state.generated_post.image_prompt:
            return state

        print(f"🎨 Generating image with prompt: {state.generated_post.image_prompt}")
        
        try:
            # Create image file path
            import uuid
            image_filename = f"generated_images/{uuid.uuid4()}.png"
            
            # Try Gemini first (better quality)
            success = generate_image_with_gemini(state.generated_post.image_prompt, image_filename)
            
            # Fallback to Pollinations.ai if Gemini fails
            if not success:
                 print("⚠️ Gemini image gen failed, trying Pollinations.ai...")
                 success = generate_image_with_pollinations(state.generated_post.image_prompt, image_filename)
            
            if success:
                state.image_path = image_filename
            
        except Exception as e:
            print(f"⚠️ Image generation failed: {e}")
            # Non-critical failure, continue without image
            
        return state

    def _human_review(self, state: WorkflowState) -> WorkflowState:
        """Break execution for human review - handled by API returning state"""
        # This node effectively just passes state, the pause happens in the router logic
        return state

    def _check_review_outcome(self, state: WorkflowState) -> str:
        """Determine next step based on user approval"""
        if state.is_approved:
            return "approved"
        elif state.feedback:
            if state.revision_count >= state.max_revisions:
                print("❌ Max revisions reached")
                return "rejected"
            return "revise"
        else:
            return "rejected"

    def _revise_content(self, state: WorkflowState) -> WorkflowState:
        """Revise content based on feedback"""
        print(f"📝 Revising content. Feedback: {state.feedback}")
        state.revision_count += 1
        
        try:
            revised_post = revise_linkedin_post(state.generated_post, state.feedback)
            state.generated_post = revised_post
            # Clear feedback for next round
            state.feedback = ""
        except Exception as e:
            state.error = f"Revision failed: {str(e)}"
            
        return state

    async def _post_to_linkedin(self, state: WorkflowState) -> WorkflowState:
        """Publish the approved post to LinkedIn using DB credentials"""
        if not state.generated_post:
            return state
            
        print("🚀 Publishing to LinkedIn...")
        
        # Verify we have user_id and db_session
        if not state.user_id or not state.db_session:
            state.error = "Missing User ID or Database Session for posting."
            return state

        try:
            # 1. Fetch credentials from DB
            user_service = UserService(state.db_session)
            credential = await user_service.get_credentials(state.user_id)
            
            if not credential:
                state.error = "No LinkedIn credentials found for this user."
                return state

            access_token = credential.access_token
            person_id = credential.linkedin_person_id

            # 2. Post using the credentials
            urn = None
            if state.image_path:
                urn = linkedin_api.post_image_content(
                    text=state.generated_post.content,
                    image_path=state.image_path,
                    access_token=access_token,
                    person_id=person_id
                )
            else:
                urn = linkedin_api.post_text_content(
                    text=state.generated_post.content,
                    access_token=access_token,
                    person_id=person_id
                )
            
            if urn:
                state.posted_to_linkedin = True
                print(f"✅ Posted successfully! URN: {urn}")
                
                # Update Post status in DB if PostService were available here, 
                # but we handle that in the Router/Service layer typically.
                # However, returning the status here allows the router to update DB.
            else:
                state.error = "LinkedIn API request failed."
                
        except Exception as e:
            state.error = f"Posting failed: {str(e)}"
            
        return state

    def run_workflow(self, topic: str, post_type: str, user_preferences: Dict, include_image: bool) -> WorkflowState:
        """Run the initial generation phase"""
        initial_state = WorkflowState(
            topic=topic, 
            post_type=post_type, 
            user_preferences=user_preferences,
            include_image=include_image
        )
        
        # Run until human review (handling async nodes is tricky in sync wrapper, 
        # normally we run this async. converting run_workflow to async in next step)
        inputs = initial_state.__dict__
        final_state_dict = self.workflow.invoke(inputs)
        
        # Convert dict back to State object
        # Note: simplistic conversion, production needs robust serialization
        result_state = WorkflowState(**{k:v for k,v in final_state_dict.items() if k in WorkflowState.__annotations__})
        return result_state

    # Note: langgraph invoke is synchronous by default unless using ainvoke.
    # But _post_to_linkedin contains async code. We must use ainvoke for the whole graph.
    
    async def run_workflow_async(self, topic: str, post_type: str, user_preferences: Dict, include_image: bool) -> WorkflowState:
        """Run workflow asynchronously"""
        initial_state = WorkflowState(
            topic=topic, 
            post_type=post_type, 
            user_preferences=user_preferences,
            include_image=include_image
        )
        logger.info(f"Initial state: {initial_state}")
        inputs = initial_state.__dict__
        # Stop at human_review
        # LangGraph behavior: depends on how interrupt is configured.
        # For simplicity in this demo, we assume the graph stops or we manually handle steps.
        # Actually our graph flow is: gen -> image -> review -> END (wait).
        # But review returns state.
        
        final_state_dict = await self.workflow.ainvoke(inputs)
        
        # Reconstruct state
        state_data = {k:v for k,v in final_state_dict.items() if k in WorkflowState.__annotations__}
        return WorkflowState(**state_data)

    async def continue_workflow_with_approval(self, state: WorkflowState, approved: bool, feedback: str = "") -> WorkflowState:
        """Continue execution after user feedback"""
        state.is_approved = approved
        state.feedback = feedback
        
        # Re-invoke workflow. LangGraph is stateful if using checkpoints, 
        # but here we are stateless between requests, so we re-invoke with updated state.
        # We need to target specific nodes or let the graph condition determine path.
        # Since we modified is_approved, the condition in _check_review_outcome will route correctly.
        
        # However, passing 'human_review' output to next step requires correct flow.
        # We can simulate the state as coming out of human_review.
        
        inputs = state.__dict__
        # We can't easily "resume" mid-graph without checkpoints in this simple setup.
        # So we create a new run where entry point skips generation?
        # Or we just call the methods directly for the final step.
        
        # For simplicity/robustness in stateless API:
        if approved:
            return await self._post_to_linkedin(state)
        elif feedback:
            # Run revision loop
            state = self._revise_content(state)
            # Return for review
            return state
        else:
            return state
