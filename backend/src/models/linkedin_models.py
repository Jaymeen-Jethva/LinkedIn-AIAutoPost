"""
Pydantic models for LinkedIn OAuth endpoints
"""
from pydantic import BaseModel
from typing import Optional


class LinkedInConnectResponse(BaseModel):
    """Response for LinkedIn connect endpoint"""
    authorization_url: str
    message: str


class LinkedInStatusResponse(BaseModel):
    """Response for LinkedIn status check"""
    connected: bool
    person_id: Optional[str] = None
    created_at: Optional[str] = None
    message: str


class LinkedInDisconnectResponse(BaseModel):
    """Response for LinkedIn disconnect endpoint"""
    success: bool
    message: str
