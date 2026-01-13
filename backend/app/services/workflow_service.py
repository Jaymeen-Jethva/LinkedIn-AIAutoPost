import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
from typing import TypedDict
from langgraph.graph.state import CompiledStateGraph
import requests
from app.services.gemini_service import generate_linkedin_post, generate_linkedin_post_with_search, revise_linkedin_post, generate_image_with_gemini, generate_image_with_pollinations, LinkedInPost
from app.services.linkedin_service import linkedin_api
from app.tools.tavily_tool import tavily_search


@dataclass
class WorkflowState:
    """State management for the LinkedIn post generation workflow"""
    topic: str = ""
    post_type: str = ""  # "ai_news" or "personal_milestone"
    user_preferences: Optional[Dict] = field(default_factory=dict)
    include_image: bool = True  # New field for image preference
    generated_post: Optional[LinkedInPost] = None
    image_path: str = ""
    user_feedback: str = ""
    revision_count: int = 0
    approved: bool = False
    posted_to_linkedin: bool = False
    error: str = ""
    nano_banana_image_url: str = ""


class LinkedInWorkflow:
    """LangGraph workflow for LinkedIn post generation and posting"""
    
    def __init__(self, use_multi_agent: bool = False):
        """
        Initialize the LinkedIn workflow
        
        Args:
            use_multi_agent: If True, use multi-agent system for content generation.
                            Falls back to single-agent if multi-agent fails.
        """
        self.use_multi_agent = use_multi_agent
        self.multi_agent_workflow = None
        
        # Initialize multi-agent workflow if requested
        if use_multi_agent:
            try:
                from app.services.multi_agent_service import MultiAgentGeminiWorkflow
                self.multi_agent_workflow = MultiAgentGeminiWorkflow()
                print("✅ Multi-agent workflow initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize multi-agent workflow: {e}")
                print("Falling back to single-agent mode")
                self.use_multi_agent = False
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> CompiledStateGraph:
        """Build the LangGraph workflow"""
        graph = StateGraph(WorkflowState)

        # Add nodes
        graph.add_node("generate_content", self._generate_content)
        graph.add_node("generate_image", self._generate_image)
        graph.add_node("await_user_approval", self._await_user_approval)
        graph.add_node("revise_content", self._revise_content)
        graph.add_node("post_to_linkedin", self._post_to_linkedin)
        graph.add_node("error_handler", self._error_handler)

        # Set entry point
        graph.set_entry_point("generate_content")

        # Conditional edges based on image preference
        graph.add_conditional_edges(
            "generate_content",
            self._image_decision,
            {
                "with_image": "generate_image",
                "without_image": "await_user_approval"
            }
        )

        graph.add_edge("generate_image", "await_user_approval")

        # Conditional edges based on user approval
        graph.add_conditional_edges(
            "await_user_approval",
            self._approval_decision,
            {
                "approved": "post_to_linkedin",
                "needs_revision": "revise_content",
                "rejected": END
            }
        )

        graph.add_edge("revise_content", "generate_content")  # Go back to content generation for revision
        graph.add_edge("post_to_linkedin", END)
        graph.add_edge("error_handler", END)

        return graph.compile()
    
    def _generate_content(self, state: WorkflowState) -> WorkflowState:
        """Generate LinkedIn post content using Gemini AI with web search enhancement"""
        try:
            print(f"Generating content for topic: {state.topic}")
            
            # Use multi-agent system if enabled and available
            if self.use_multi_agent and self.multi_agent_workflow:
                return self._generate_content_multi_agent(state)
            
            # Standard single-agent generation
            return self._generate_content_single_agent(state)
            
        except Exception as e:
            state.error = f"Content generation failed: {str(e)}"
            print(f"Error generating content: {e}")
            return state
    
    def _generate_content_multi_agent(self, state: WorkflowState) -> WorkflowState:
        """Generate content using multi-agent collaborative system"""
        try:
            print("🚀 Using multi-agent system for content generation...")
            
            # Get search results if available
            search_results = []
            if tavily_search.is_available():
                if state.post_type == "ai_news":
                    search_results = tavily_search.search_ai_news(state.topic)
                else:
                    search_results = tavily_search.search_technical_info(state.topic)
                print(f"Web search found {len(search_results)} results")
            
            # Use multi-agent workflow
            result = self.multi_agent_workflow.generate_post(
                topic=state.topic,
                post_type=state.post_type,
                search_results=search_results,
                user_preferences=state.user_preferences,
                include_image=state.include_image
            )
            
            # Convert to LinkedInPost format
            state.generated_post = LinkedInPost(
                content=result["content"],
                hashtags=result["hashtags"],
                image_prompt=result.get("image_prompt"),
                post_type=result["post_type"]
            )
            
            print("✅ Multi-agent content generation complete!")
            return state
            
        except Exception as e:
            print(f"⚠️ Multi-agent generation failed: {e}")
            print("Falling back to single-agent generation...")
            # Fallback to single-agent
            return self._generate_content_single_agent(state)
    
    def _generate_content_single_agent(self, state: WorkflowState) -> WorkflowState:
        """Standard single-agent content generation (original method)"""
        try:
            # Check if Tavily search is available for enhanced content
            if tavily_search.is_available():
                print("Using web search enhancement for content generation")
                generated_post, search_results = generate_linkedin_post_with_search(
                    topic=state.topic,
                    post_type=state.post_type,
                    user_preferences=state.user_preferences or {},
                    include_image=state.include_image
                )
                print(f"Content generated with {len(search_results)} web search results")
            else:
                print("Tavily search not available, using standard content generation")
                generated_post = generate_linkedin_post(
                    topic=state.topic,
                    post_type=state.post_type,
                    user_preferences=state.user_preferences or {},
                    include_image=state.include_image,
                    use_web_search=False
                )
                print("Content generated without web search enhancement")

            state.generated_post = generated_post
            print("Content generated successfully")
            return state
        except Exception as e:
            state.error = f"Content generation failed: {str(e)}"
            print(f"Error generating content: {e}")
            return state
    
    def _generate_image(self, state: WorkflowState) -> WorkflowState:
        """Generate image for the post"""
        try:
            if not state.generated_post:
                state.error = "No generated post available for image creation"
                return state
            
            print("Generating image...")
            
            # Try Gemini image generation first
            image_path = f"generated_images/post_image_{state.revision_count}.png"
            os.makedirs("generated_images", exist_ok=True)
            
            gemini_success = generate_image_with_gemini(
                state.generated_post.image_prompt, 
                image_path
            )
            
            if gemini_success:
                state.image_path = image_path
                print(f"Image generated with Gemini and saved to {image_path}")
            else:
                # Fallback to Pollinations.ai
                print("Gemini image generation failed, trying Pollinations.ai...")
                pollinations_success = generate_image_with_pollinations(
                    state.generated_post.image_prompt,
                    image_path
                )
                if pollinations_success:
                    state.image_path = image_path
                    print(f"Image generated with Pollinations.ai and saved to {image_path}")
                else:
                    print("All image generation methods failed, continuing without image")
                    state.image_path = ""
            
            return state
        except Exception as e:
            state.error = f"Image generation failed: {str(e)}"
            print(f"Error generating image: {e}")
            return state
    
    def _await_user_approval(self, state: WorkflowState) -> WorkflowState:
        """Wait for user approval - this will be handled by the web interface"""
        print("Awaiting user approval...")
        # This node represents the pause for user interaction
        # The actual approval logic is handled by the web interface
        return state
    
    def _image_decision(self, state: WorkflowState) -> str:
        """Decide whether to generate image or skip it"""
        if state.include_image:
            return "with_image"
        else:
            print("Skipping image generation as requested by user")
            return "without_image"

    def _approval_decision(self, state: WorkflowState) -> str:
        """Decide next step based on user approval"""
        if state.approved:
            return "approved"
        elif state.user_feedback:
            return "needs_revision"
        else:
            return "rejected"
    
    def _revise_content(self, state: WorkflowState) -> WorkflowState:
        """Revise content based on user feedback"""
        try:
            if not state.user_feedback:
                state.error = "No feedback provided for revision"
                return state
            
            print(f"Revising content based on feedback: {state.user_feedback}")
            revised_post = revise_linkedin_post(state.generated_post, state.user_feedback)
            state.generated_post = revised_post
            state.revision_count += 1
            state.user_feedback = ""  # Clear feedback after revision
            print("Content revised successfully")
            return state
        except Exception as e:
            state.error = f"Content revision failed: {str(e)}"
            print(f"Error revising content: {e}")
            return state
    
    def _post_to_linkedin(self, state: WorkflowState) -> WorkflowState:
        """Post the approved content to LinkedIn"""
        try:
            print("Posting to LinkedIn...")
            
            if not linkedin_api.is_configured():
                print("LinkedIn API not configured, simulating post...")
                print("To enable real LinkedIn posting, add LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID to environment variables")
                print(f"Content: {state.generated_post.content}")
                print(f"Hashtags: {', '.join(state.generated_post.hashtags)}")
                print(f"Image: {state.image_path}")
                state.posted_to_linkedin = True
                print("Post successfully 'posted' to LinkedIn (simulation)")
                return state
            
            # Post with image if available, otherwise text only
            if state.image_path and os.path.exists(state.image_path):
                result = linkedin_api.post_content_with_image(
                    content=state.generated_post.content,
                    image_path=state.image_path,
                    hashtags=state.generated_post.hashtags
                )
            else:
                result = linkedin_api.post_text_content(
                    content=state.generated_post.content,
                    hashtags=state.generated_post.hashtags
                )
            
            if result.get("success"):
                state.posted_to_linkedin = True
                print(f"✅ {result.get('message', 'Posted successfully!')}")
            else:
                state.error = result.get("error", "Unknown LinkedIn API error")
                print(f"❌ LinkedIn posting failed: {state.error}")
            
            return state
        except Exception as e:
            state.error = f"LinkedIn posting failed: {str(e)}"
            print(f"Error posting to LinkedIn: {e}")
            return state
    
    def _error_handler(self, state: WorkflowState) -> WorkflowState:
        """Handle errors in the workflow"""
        print(f"Error in workflow: {state.error}")
        return state
    
    def run_workflow(self, topic: str, post_type: str, user_preferences: Dict = None, include_image: bool = True) -> WorkflowState:
        """Run the complete workflow"""
        initial_state = WorkflowState(
            topic=topic,
            post_type=post_type,
            user_preferences=user_preferences or {},
            include_image=include_image
        )
        
        try:
            # Run until user approval is needed
            result = self.workflow.invoke(initial_state)
            return WorkflowState(**result) if isinstance(result, dict) else result
        except Exception as e:
            initial_state.error = f"Workflow execution failed: {str(e)}"
            return initial_state
    
    def continue_workflow_with_approval(self, state: WorkflowState, approved: bool, feedback: str = "") -> WorkflowState:
        """Continue workflow after user provides approval/feedback"""
        state.approved = approved
        state.user_feedback = feedback
        
        try:
            # Continue from where we left off
            result = self.workflow.invoke(state)
            return WorkflowState(**result) if isinstance(result, dict) else result
        except Exception as e:
            state.error = f"Workflow continuation failed: {str(e)}"
            return state


# Global workflow instance
linkedin_workflow = LinkedInWorkflow()
