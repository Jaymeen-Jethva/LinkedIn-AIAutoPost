"""
Pydantic models for Post generation endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


# Input validation constants
MIN_TOPIC_LENGTH = 10
MAX_TOPIC_LENGTH = 500
ALLOWED_POST_TYPES = ["ai_news", "personal_milestone"]


class PostRequest(BaseModel):
    """Request body for generating a new post"""
    topic: str = Field(..., min_length=MIN_TOPIC_LENGTH, max_length=MAX_TOPIC_LENGTH)
    post_type: str  # "ai_news" or "personal_milestone"
    user_preferences: Optional[Dict] = {}
    include_image: bool = True
    use_multi_agent: bool = False


class ApprovalRequest(BaseModel):
    """Request body for approving or rejecting a post"""
    session_id: str
    approved: bool
    feedback: Optional[str] = ""


class PostResponse(BaseModel):
    """Response containing generated post content"""
    session_id: str
    content: str
    hashtags: List[str]
    image_path: Optional[str] = None
    image_prompt: Optional[str] = None
    post_type: str
    multi_agent_used: bool = False
    revised: bool = False


class ApprovalResponse(BaseModel):
    """Response for post approval"""
    success: bool
    message: str
    posted_to_linkedin: Optional[bool] = None
