import os
import json
import logging
from typing import Dict, Any, List, Optional, Annotated
import operator
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from jinja2 import Environment, FileSystemLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Helper Functions ====================

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

def render_messages_from_template(agent_name: str, **kwargs) -> List[Any]:
    """
    Load prompt template from .jinja2 file, render it with context,
    and split into System and Human messages.
    """
    try:
        # Assuming app is running from backend directory
        prompts_dir = os.path.join(os.getcwd(), "app", "agent_prompts")
        env = Environment(loader=FileSystemLoader(prompts_dir))
        template = env.get_template(f"{agent_name}.jinja2")
        
        # Render the full text with variables
        full_text = template.render(**kwargs)
        
        # Split into System and Human parts
        parts = full_text.split("---HUMAN_INPUT_START---")
        
        if len(parts) == 2:
            system_text = parts[0].strip()
            human_text = parts[1].strip()
            return [
                SystemMessage(content=system_text),
                HumanMessage(content=human_text)
            ]
        else:
            logger.warning(f"Template {agent_name} missing separator. Returning as HumanMessage.")
            return [HumanMessage(content=full_text)]

    except Exception as e:
        logger.error(f"Failed to render prompt for {agent_name}: {e}")
        return [HumanMessage(content=f"Error loading prompt: {e}")]

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
        
        if state.search_results:
            search_context = "\n\n".join([
                f"Source {i+1}: {r.get('title', 'Untitled')}\n{r.get('content', '')}"
                for i, r in enumerate(state.search_results[:5])
            ])
        else:
            search_context = "No external search results available. Use your knowledge to provide insights."
        
        messages = render_messages_from_template(
            "research_agent",
            post_type=state.post_type,
            topic=state.topic,
            search_context=search_context,
            user_preferences=state.user_preferences
        )
        
        response = self.llm.invoke(messages)
        
        # Parse response
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
            state.research_summary = result.get("research_summary", "")
            state.key_insights = result.get("key_insights", [])
        except Exception as e:
            logger.warning(f"Failed to parse research response as JSON: {e}")
            state.research_summary = content if content else "Research completed."
            state.key_insights = []
        
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
        
        messages = render_messages_from_template(
            "strategy_agent",
            topic=state.topic,
            post_type=state.post_type,
            research_summary=state.research_summary,
            key_insights="\n".join(state.key_insights) if state.key_insights else "No specific insights available",
            user_preferences=state.user_preferences
        )
        
        response = self.llm.invoke(messages)
        
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
            
            state.target_audience = str(result.get("target_audience", ""))
            state.tone_guidelines = str(result.get("tone_guidelines", ""))
            
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
        
        revision_context = ""
        if state.revision_count > 0 and state.editor_feedback:
            revision_context = f"""
            
            IMPORTANT - This is revision #{state.revision_count}. Previous editor feedback:
            {state.editor_feedback}
            
            Please address this feedback in your revised draft.
            """
        
        messages = render_messages_from_template(
            "writer_agent",
            post_type=state.post_type,
            topic=state.topic,
            content_strategy=state.content_strategy,
            content_outline=state.content_outline,
            key_insights="\n".join(state.key_insights) if state.key_insights else "No specific insights",
            target_audience=state.target_audience,
            tone_guidelines=state.tone_guidelines,
            revision_context=revision_context
        )
        
        response = self.llm.invoke(messages)
        
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
        
        messages = render_messages_from_template(
            "editor_agent",
            draft_content=state.draft_content,
            topic=state.topic,
            content_strategy=state.content_strategy,
            revision_count=state.revision_count,
            max_revisions=state.max_revisions
        )
        
        response = self.llm.invoke(messages)
        
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
            state.editor_feedback = ""
            state.revised_content = state.draft_content
            state.needs_revision = False
        
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
        
        messages = render_messages_from_template(
            "seo_agent",
            content=state.revised_content,
            topic=state.topic,
            post_type=state.post_type,
            key_insights="\n".join(state.key_insights[:3]) if state.key_insights else "No specific insights"
        )
        
        response = self.llm.invoke(messages)
        
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
        
        messages = render_messages_from_template(
            "visual_designer_agent",
            content=state.revised_content,
            topic=state.topic,
            post_type=state.post_type,
            key_insights=", ".join(state.key_insights[:3]) if state.key_insights else state.topic
        )
        
        response = self.llm.invoke(messages)
        
        content = extract_clean_content(response)
        state.image_prompt = content.strip()
        state.messages.append(AIMessage(content=f"Visual concept created"))
        logger.info(f"✅ {self.name}: Image prompt generated ({len(state.image_prompt)} chars)")
        return state
