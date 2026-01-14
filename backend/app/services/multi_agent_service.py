"""
Multi-Agent LinkedIn Post Generation System using LangGraph and LangChain with Gemini
This implements a sophisticated agent collaboration system for high-quality content generation.
Uses ONLY the Gemini API via langchain-google-genai.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Annotated
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import operator

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Helper for Gemini content extraction
def extract_clean_content(response: Any) -> str:
    """Robustly extract string content from Gemini/LangChain response"""
    if hasattr(response, 'content'):
        content = response.content
    else:
        content = str(response)
        
    # Handle list of parts (common in newer Gemini versions)
    if isinstance(content, list):
        # Join text parts
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and 'text' in part:
                text_parts.append(part['text'])
            elif hasattr(part, 'text'):
                text_parts.append(part.text)
        content = "\n".join(text_parts)
        
    return str(content)


# ==================== State Definitions ====================

class AgentState(BaseModel):
    """Shared state across all agents"""
    # Input
    topic: str = ""
    post_type: str = ""  # "ai_news" or "personal_milestone"
    user_preferences: Dict = Field(default_factory=dict)
    include_image: bool = True
    
    # Research phase
    search_results: List[Dict] = Field(default_factory=list)
    research_summary: str = ""
    key_insights: List[str] = Field(default_factory=list)
    
    # Strategy phase
    content_strategy: str = ""
    target_audience: str = ""
    tone_guidelines: str = ""
    content_outline: str = ""
    
    # Writing phase
    draft_content: str = ""
    
    # Editing phase
    editor_feedback: str = ""
    revised_content: str = ""
    
    # SEO phase
    hashtags: List[str] = Field(default_factory=list)
    seo_notes: str = ""
    
    # Visual phase
    image_prompt: str = ""
    
    # Final output
    final_post: Optional[Dict] = None
    
    # Workflow control
    revision_count: int = 0
    max_revisions: int = 2
    needs_revision: bool = False
    error: str = ""
    
    # Message history for agent communication
    messages: Annotated[List[Any], operator.add] = Field(default_factory=list)


# ==================== Agent Definitions ====================

class ResearchAgent:
    """Agent responsible for gathering and synthesizing information"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Research Agent"
    
    def research(self, state: AgentState) -> AgentState:
        """Conduct research and synthesize findings"""
        logger.info(f"🔍 {self.name}: Analyzing search results...")
        
        # If you have search results from Tavily
        if state.search_results:
            search_context = "\n\n".join([
                f"Source {i+1}: {r.get('title', 'Untitled')}\n{r.get('content', '')}"
                for i, r in enumerate(state.search_results[:5])
            ])
        else:
            search_context = "No external search results available. Use your knowledge to provide insights."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research analyst specializing in {post_type} content.
            Your job is to analyze information and extract key insights that would make compelling LinkedIn content.
            
            Focus on:
            1. Most recent and relevant developments
            2. Unique angles or perspectives
            3. Data points and statistics that support the narrative
            4. Contrarian or thought-provoking insights
            
            Provide a concise research summary and 3-5 key insights."""),
            ("human", """Topic: {topic}
            
            Available Information:
            {search_context}
            
            User Preferences: {user_preferences}
            
            Provide your research summary and key insights in JSON format:
            {{
                "research_summary": "...",
                "key_insights": ["insight1", "insight2", "insight3"]
            }}""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "topic": state.topic,
            "post_type": state.post_type,
            "search_context": search_context,
            "user_preferences": state.user_preferences
        })
        
        # Parse response
        try:
            # Handle AIMessage content
            content = extract_clean_content(response)
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            result = json.loads(content.strip())
            state.research_summary = result.get("research_summary", "")
            state.key_insights = result.get("key_insights", [])
        except Exception as e:
            logger.warning(f"Failed to parse research response as JSON: {e}")
            state.research_summary = content if content else "Research completed."
            state.key_insights = []
        
        # Safely log truncated summary
        summary_preview = str(state.research_summary)[:100] if state.research_summary else "No summary"
        state.messages.append(AIMessage(content=f"Research complete: {summary_preview}..."))
        logger.info(f"✅ {self.name}: Research summary generated with {len(state.key_insights)} insights")
        return state


class StrategyAgent:
    """Agent responsible for content strategy and planning"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Strategy Agent"
    
    def strategize(self, state: AgentState) -> AgentState:
        """Develop content strategy"""
        logger.info(f"📋 {self.name}: Developing content strategy...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a LinkedIn content strategist with expertise in viral professional content.
            Your job is to create a winning content strategy based on research insights.
            
            Consider:
            1. Target audience on LinkedIn (professionals, decision-makers, industry peers)
            2. Optimal post structure (hook, body, call-to-action)
            3. Tone that balances professionalism with authenticity
            4. Engagement triggers (questions, controversy, value)
            
            Provide a detailed content strategy and outline."""),
            ("human", """Topic: {topic}
            Post Type: {post_type}
            
            Research Summary:
            {research_summary}
            
            Key Insights:
            {key_insights}
            
            User Preferences: {user_preferences}
            
            Create a content strategy in JSON format:
            {{
                "target_audience": "...",
                "tone_guidelines": "...",
                "content_outline": "...",
                "engagement_strategy": "..."
            }}""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "topic": state.topic,
            "post_type": state.post_type,
            "research_summary": state.research_summary,
            "key_insights": "\n".join(state.key_insights) if state.key_insights else "No specific insights available",
            "user_preferences": state.user_preferences
        })
        
        try:
            content = extract_clean_content(response)
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            result = json.loads(content.strip())
            
            # Robustly handle types
            state.target_audience = str(result.get("target_audience", ""))
            state.tone_guidelines = str(result.get("tone_guidelines", ""))
            
            # Handle content_outline - ensure string
            outline = result.get("content_outline", "")
            if isinstance(outline, (dict, list)):
                state.content_outline = json.dumps(outline, indent=2)
            else:
                state.content_outline = str(outline)
                
            state.content_strategy = json.dumps(result)
        except Exception as e:
            logger.warning(f"Failed to parse strategy response as JSON: {e}")
            state.content_strategy = content if content else "Strategy developed."
            state.content_outline = content if content else "No outline."
        
        # Safely log truncated outline
        outline_preview = str(state.content_outline)[:100] if state.content_outline else "Outline created"
        audience_preview = str(state.target_audience)[:50] if state.target_audience else "General audience"
        state.messages.append(AIMessage(content=f"Strategy developed: {outline_preview}..."))
        logger.info(f"✅ {self.name}: Strategy complete for audience: {audience_preview}...")
        return state


class WriterAgent:
    """Agent responsible for crafting the actual content"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Writer Agent"
    
    def write(self, state: AgentState) -> AgentState:
        """Write the LinkedIn post"""
        logger.info(f"✍️ {self.name}: Writing content...")
        
        # Include editor feedback if this is a revision
        revision_context = ""
        if state.revision_count > 0 and state.editor_feedback:
            revision_context = f"""
            
            IMPORTANT - This is revision #{state.revision_count}. Previous editor feedback:
            {state.editor_feedback}
            
            Please address this feedback in your revised draft.
            """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert LinkedIn copywriter known for creating viral, engaging professional content.
            
            Your writing style:
            - Compelling hooks that stop scrolling (first line is CRITICAL)
            - Clear, concise paragraphs (2-3 lines each)
            - Strategic use of line breaks for readability
            - Conversational yet professional tone
            - Data-driven when possible
            - Authentic storytelling
            - Strong call-to-action at the end
            
            Length: 150-300 words for {post_type}
            
            DO NOT include hashtags - another agent will handle that.
            DO NOT use generic openings like "I'm excited to share" or "Thrilled to announce"."""),
            ("human", """Topic: {topic}
            
            Content Strategy:
            {content_strategy}
            
            Content Outline:
            {content_outline}
            
            Key Insights to Incorporate:
            {key_insights}
            
            Target Audience: {target_audience}
            Tone: {tone_guidelines}
            {revision_context}
            
            Write a compelling LinkedIn post following the strategy and outline.
            Return ONLY the post content, no hashtags, no explanations.""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "topic": state.topic,
            "post_type": state.post_type,
            "content_strategy": state.content_strategy,
            "content_outline": state.content_outline,
            "key_insights": "\n".join(state.key_insights) if state.key_insights else "No specific insights",
            "target_audience": state.target_audience,
            "tone_guidelines": state.tone_guidelines,
            "revision_context": revision_context
        })
        
        
        content = extract_clean_content(response)
        state.draft_content = content.strip()
        state.messages.append(AIMessage(content=f"Draft written: {len(state.draft_content)} characters"))
        logger.info(f"✅ {self.name}: Draft complete ({len(state.draft_content)} chars)")
        return state


class EditorAgent:
    """Agent responsible for reviewing and improving content"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Editor Agent"
    
    def edit(self, state: AgentState) -> AgentState:
        """Review and critique the content"""
        logger.info(f"📝 {self.name}: Reviewing content...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior editor specializing in LinkedIn content.
            Your job is to critique and improve the draft.
            
            Evaluate:
            1. Hook strength - does it grab attention in the first line?
            2. Clarity and readability - are paragraphs concise?
            3. Value proposition - what does the reader gain?
            4. Authenticity and credibility
            5. Call-to-action effectiveness
            6. Grammar and style
            
            Be constructive but also know when content is GOOD ENOUGH.
            Don't nitpick perfect content - approve it.
            
            Provide either:
            - "APPROVED" if the content is good or excellent
            - Specific, actionable feedback for improvement (only if genuinely needed)"""),
            ("human", """Draft Content:
            {draft_content}
            
            Original Topic: {topic}
            Strategy: {content_strategy}
            Revision Count: {revision_count}/{max_revisions}
            
            Review this content. If it needs significant improvement, provide specific feedback.
            If it's good enough or excellent, respond with APPROVED.
            
            Format your response as JSON:
            {{
                "status": "APPROVED" or "NEEDS_REVISION",
                "feedback": "...",
                "revised_content": "..." (only if you made direct improvements, otherwise empty string)
            }}""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "draft_content": state.draft_content,
            "topic": state.topic,
            "content_strategy": state.content_strategy,
            "revision_count": state.revision_count,
            "max_revisions": state.max_revisions
        })
        
        try:
            content = extract_clean_content(response)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            result = json.loads(content.strip())
            status = result.get("status", "APPROVED")
            state.editor_feedback = result.get("feedback", "")
            
            if status == "APPROVED" or "APPROVED" in status.upper():
                # Use revised content if editor provided improvements, otherwise use draft
                revised = result.get("revised_content", "")
                state.revised_content = revised if revised and len(revised) > 50 else state.draft_content
                state.needs_revision = False
                logger.info(f"✅ {self.name}: Content APPROVED!")
            else:
                revised = result.get("revised_content", "")
                state.revised_content = revised if revised and len(revised) > 50 else state.draft_content
                state.needs_revision = True
                state.revision_count += 1
                logger.info(f"🔄 {self.name}: Revision requested ({state.revision_count}/{state.max_revisions})")
        except Exception as e:
            logger.warning(f"Failed to parse editor response as JSON: {e}")
            # Default to approved if we can't parse
            state.editor_feedback = ""
            state.revised_content = state.draft_content
            state.needs_revision = False
        
        # Safely log truncated feedback
        feedback_preview = str(state.editor_feedback)[:100] if state.editor_feedback else "Approved"
        state.messages.append(AIMessage(content=f"Editing complete: {feedback_preview}..."))
        return state


class SEOAgent:
    """Agent responsible for hashtags and LinkedIn optimization"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "SEO Agent"
    
    def optimize(self, state: AgentState) -> AgentState:
        """Generate hashtags and SEO recommendations"""
        logger.info(f"🏷️ {self.name}: Optimizing for LinkedIn algorithm...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a LinkedIn SEO specialist and algorithm expert.
            Your job is to select hashtags that maximize reach and engagement.
            
            Guidelines:
            1. Mix of popular (100K+ posts) and niche hashtags
            2. 3-5 hashtags maximum (LinkedIn best practice)
            3. Relevant to both content and target audience
            4. Include trending industry-specific tags
            5. Avoid overly generic hashtags like #success or #motivation
            
            Return hashtags WITHOUT the # symbol."""),
            ("human", """Content:
            {content}
            
            Topic: {topic}
            Post Type: {post_type}
            Key Insights: {key_insights}
            
            Generate 3-5 optimal hashtags for this LinkedIn post.
            
            Return JSON:
            {{
                "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
                "seo_notes": "brief explanation of hashtag strategy"
            }}""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "content": state.revised_content,
            "topic": state.topic,
            "post_type": state.post_type,
            "key_insights": "\n".join(state.key_insights[:3]) if state.key_insights else "No specific insights"
        })
        
        try:
            content = extract_clean_content(response)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            result = json.loads(content.strip())
            state.hashtags = result.get("hashtags", [])
            state.seo_notes = result.get("seo_notes", "")
        except Exception as e:
            logger.warning(f"Failed to parse SEO response as JSON: {e}")
            # Fallback hashtags based on post type
            if state.post_type == "ai_news":
                state.hashtags = ["AI", "ArtificialIntelligence", "Technology", "Innovation", "FutureOfWork"]
            else:
                state.hashtags = ["CareerGrowth", "ProfessionalDevelopment", "Leadership", "Success"]
        
        state.messages.append(AIMessage(content=f"SEO optimization complete: {len(state.hashtags)} hashtags"))
        logger.info(f"✅ {self.name}: Generated {len(state.hashtags)} hashtags")
        return state


class VisualDesignerAgent:
    """Agent responsible for image generation prompts"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Visual Designer Agent"
    
    def design(self, state: AgentState) -> AgentState:
        """Create detailed image generation prompt"""
        if not state.include_image:
            logger.info(f"🎨 {self.name}: Image generation skipped per user preference")
            return state
            
        logger.info(f"🎨 {self.name}: Creating visual concept...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a creative director specializing in LinkedIn visual content.
            Your job is to create detailed image generation prompts that will result in 
            professional, eye-catching visuals that complement the post content.
            
            Guidelines:
            1. Professional and polished aesthetic
            2. Relevant to the content theme
            3. Attention-grabbing but not gimmicky
            4. High quality, modern style
            5. Avoid text in images (poor LinkedIn practice)
            6. Use vibrant but professional colors
            
            Be specific about: composition, lighting, style, colors, mood."""),
            ("human", """Post Content:
            {content}
            
            Topic: {topic}
            Post Type: {post_type}
            Key Themes: {key_insights}
            
            Create a detailed image generation prompt (100-150 words) that will produce
            a professional LinkedIn-worthy visual for this post.
            
            Return only the image prompt text, no JSON or other formatting.""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "content": state.revised_content,
            "topic": state.topic,
            "post_type": state.post_type,
            "key_insights": ", ".join(state.key_insights[:3]) if state.key_insights else state.topic
        })
        
        
        content = extract_clean_content(response)
        state.image_prompt = content.strip()
        state.messages.append(AIMessage(content=f"Visual concept created"))
        logger.info(f"✅ {self.name}: Image prompt generated ({len(state.image_prompt)} chars)")
        return state


# ==================== Workflow Orchestration ====================

class MultiAgentGeminiWorkflow:
    """Orchestrates the multi-agent workflow using Gemini models"""
    
    def __init__(
        self,
        fast_model: str = "gemini-2.5-flash",
        powerful_model: str = "gemini-2.5-pro"
    ):
        """
        Initialize with Gemini models
        
        Args:
            fast_model: Model for research/strategy/SEO (speed-optimized)
            powerful_model: Model for writing/editing (quality-optimized)
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Initialize LLMs with different models for different tasks
        self.fast_llm = ChatGoogleGenerativeAI(
            model=fast_model,
            temperature=0.5,
            google_api_key=api_key,
            convert_system_message_to_human=True  # Gemini compatibility
        )
        
        self.powerful_llm = ChatGoogleGenerativeAI(
            model=powerful_model,
            temperature=0.7,
            google_api_key=api_key,
            convert_system_message_to_human=True  # Gemini compatibility
        )
        
        # Initialize agents with appropriate LLMs
        self.research_agent = ResearchAgent(self.fast_llm)
        self.strategy_agent = StrategyAgent(self.fast_llm)
        self.writer_agent = WriterAgent(self.powerful_llm)
        self.editor_agent = EditorAgent(self.powerful_llm)
        self.seo_agent = SEOAgent(self.fast_llm)
        self.visual_agent = VisualDesignerAgent(self.fast_llm)
        
        # Build workflow
        self.workflow = self._build_workflow()
        
        logger.info(f"Multi-agent workflow initialized with {fast_model} (fast) and {powerful_model} (powerful)")
    
    def _build_workflow(self):
        """Build the multi-agent LangGraph workflow"""
        graph = StateGraph(AgentState)
        
        # Add agent nodes
        graph.add_node("research", self.research_agent.research)
        graph.add_node("strategy", self.strategy_agent.strategize)
        graph.add_node("write", self.writer_agent.write)
        graph.add_node("edit", self.editor_agent.edit)
        graph.add_node("seo", self.seo_agent.optimize)
        graph.add_node("visual", self.visual_agent.design)
        graph.add_node("finalize", self._finalize_post)
        
        # Define the flow
        graph.set_entry_point("research")
        graph.add_edge("research", "strategy")
        graph.add_edge("strategy", "write")
        graph.add_edge("write", "edit")
        
        # Conditional edge based on editor approval
        graph.add_conditional_edges(
            "edit",
            self._should_revise,
            {
                "revise": "write",  # Go back to writer
                "continue": "seo"
            }
        )
        
        graph.add_edge("seo", "visual")
        graph.add_edge("visual", "finalize")
        graph.add_edge("finalize", END)
        
        return graph.compile()
    
    def _should_revise(self, state: AgentState) -> str:
        """Decide if content needs revision"""
        if state.needs_revision and state.revision_count < state.max_revisions:
            logger.info(f"🔄 Revision needed (attempt {state.revision_count}/{state.max_revisions})")
            return "revise"
        return "continue"
    
    def _finalize_post(self, state: AgentState) -> AgentState:
        """Compile the final post"""
        logger.info(f"✅ Finalizing post...")
        
        state.final_post = {
            "content": state.revised_content,
            "hashtags": state.hashtags,
            "image_prompt": state.image_prompt if state.include_image else None,
            "post_type": state.post_type,
            "metadata": {
                "research_summary": state.research_summary,
                "content_strategy": state.content_strategy,
                "revision_count": state.revision_count,
                "seo_notes": state.seo_notes,
                "agent_messages": len(state.messages)
            }
        }
        
        return state
    
    def generate_post(
        self,
        topic: str,
        post_type: str,
        search_results: List[Dict] = None,
        user_preferences: Dict = None,
        include_image: bool = True
    ) -> Dict:
        """
        Generate a LinkedIn post using the multi-agent system
        
        Args:
            topic: The topic for the post
            post_type: "ai_news" or "personal_milestone"
            search_results: Optional web search results from Tavily
            user_preferences: Optional user preferences
            include_image: Whether to generate image prompt
            
        Returns:
            Dict containing the final post and metadata
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Multi-Agent LinkedIn Post Generation (Gemini)")
        logger.info(f"Topic: {topic}")
        logger.info(f"Type: {post_type}")
        logger.info(f"{'='*60}")
        
        initial_state = AgentState(
            topic=topic,
            post_type=post_type,
            search_results=search_results or [],
            user_preferences=user_preferences or {},
            include_image=include_image
        )
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✨ Post Generation Complete!")
        logger.info(f"Revisions: {final_state.get('revision_count', 0)}")
        logger.info(f"{'='*60}\n")
        
        return final_state.get('final_post')


# ==================== Usage Example ====================

if __name__ == "__main__":
    # Example usage
    workflow = MultiAgentGeminiWorkflow(
        fast_model="gemini-2.5-flash",
        powerful_model="gemini-2.5-pro"
    )
    
    # Generate a post
    result = workflow.generate_post(
        topic="The impact of AI agents on software development",
        post_type="ai_news",
        user_preferences={"tone": "thought-provoking", "length": "medium"},
        include_image=True
    )
    
    print("\n📄 FINAL POST:")
    print(result["content"])
    print(f"\n🏷️ Hashtags: {', '.join(result['hashtags'])}")
    if result["image_prompt"]:
        print(f"\n🎨 Image Prompt: {result['image_prompt'][:100]}...")
