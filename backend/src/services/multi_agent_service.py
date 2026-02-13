"""
Multi-Agent LinkedIn Post Generation System using LangGraph and LangChain with Gemini
This implements a sophisticated agent collaboration system for high-quality content generation.
Uses ONLY the Gemini API via langchain-google-genai.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from dotenv import load_dotenv

from src.services.agent_class import (
    AgentState, 
    ResearchAgent, 
    StrategyAgent, 
    WriterAgent, 
    EditorAgent, 
    SEOAgent, 
    VisualDesignerAgent,
    extract_clean_content
)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
