"""
Post Generation Router

Handles LinkedIn post generation workflow:
- /generate-post - Generate a new post
- /approve-post - Approve or request revision
"""
import re
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.post_models import (
    PostRequest,
    ApprovalRequest,
    PostResponse,
    ApprovalResponse,
    MIN_TOPIC_LENGTH,
    MAX_TOPIC_LENGTH,
    ALLOWED_POST_TYPES
)
from app.services.workflow_service import LinkedInWorkflow

router = APIRouter()

# In-memory storage for workflow states (in production, use a proper database)
workflow_sessions = {}  # {session_id: {"state": WorkflowState, "workflow": LinkedInWorkflow}}

# Characters that might cause issues in prompts
DANGEROUS_CHARS_PATTERN = r'[<>{}|\\^`]'


def validate_topic(topic: str) -> tuple[bool, str]:
    """
    Validate topic input for length and dangerous characters.
    Returns (is_valid, error_message)
    """
    if not topic or not topic.strip():
        return False, "Topic cannot be empty"
    
    if len(topic.strip()) < MIN_TOPIC_LENGTH:
        return False, f"Topic must be at least {MIN_TOPIC_LENGTH} characters long"
    
    if len(topic) > MAX_TOPIC_LENGTH:
        return False, f"Topic must not exceed {MAX_TOPIC_LENGTH} characters"
    
    if re.search(DANGEROUS_CHARS_PATTERN, topic):
        return False, "Topic contains invalid characters. Please remove: < > { } | \\ ^ `"
    
    return True, ""


def validate_post_type(post_type: str) -> tuple[bool, str]:
    """
    Validate post type against allowed values.
    Returns (is_valid, error_message)
    """
    if post_type not in ALLOWED_POST_TYPES:
        return False, f"Invalid post type. Must be one of: {', '.join(ALLOWED_POST_TYPES)}"
    return True, ""


@router.post("/generate-post")
async def generate_post(post_request: PostRequest):
    """Generate a LinkedIn post based on user input"""
    # Validate input before processing
    is_valid, error_msg = validate_topic(post_request.topic)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    is_valid, error_msg = validate_post_type(post_request.post_type)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        # Create a session ID
        session_id = str(uuid.uuid4())
        
        # Create workflow instance (with optional multi-agent mode)
        workflow_instance = LinkedInWorkflow(use_multi_agent=post_request.use_multi_agent)
        
        # Run the workflow until user approval is needed
        result_state = workflow_instance.run_workflow(
            topic=post_request.topic.strip(),
            post_type=post_request.post_type,
            user_preferences=post_request.user_preferences,
            include_image=post_request.include_image
        )
        
        # Store the state AND workflow instance for later continuation
        workflow_sessions[session_id] = {
            "state": result_state,
            "workflow": workflow_instance
        }
        
        if result_state.error:
            raise HTTPException(status_code=500, detail=result_state.error)
        
        # Return the generated content for user review
        response_data = {
            "session_id": session_id,
            "content": result_state.generated_post.content if result_state.generated_post else "",
            "hashtags": result_state.generated_post.hashtags if result_state.generated_post else [],
            "image_path": result_state.image_path,
            "image_prompt": result_state.generated_post.image_prompt if result_state.generated_post else "",
            "post_type": result_state.post_type,
            "multi_agent_used": post_request.use_multi_agent
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve-post")
async def approve_post(approval_request: ApprovalRequest):
    """Handle user approval or feedback for the generated post"""
    try:
        session_id = approval_request.session_id
        
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = workflow_sessions[session_id]
        current_state = session_data["state"]
        workflow_instance = session_data["workflow"]
        
        # Continue the workflow with user decision
        final_state = workflow_instance.continue_workflow_with_approval(
            state=current_state,
            approved=approval_request.approved,
            feedback=approval_request.feedback or ""
        )
        
        # Update the stored state
        workflow_sessions[session_id]["state"] = final_state
        
        if final_state.error:
            raise HTTPException(status_code=500, detail=final_state.error)
        
        # If revision was requested, return the updated content
        if approval_request.feedback and not approval_request.approved:
            response_data = {
                "session_id": session_id,
                "content": final_state.generated_post.content if final_state.generated_post else "",
                "hashtags": final_state.generated_post.hashtags if final_state.generated_post else [],
                "image_path": final_state.image_path,
                "image_prompt": final_state.generated_post.image_prompt if final_state.generated_post else "",
                "post_type": final_state.post_type,
                "revised": True
            }
            return JSONResponse(content=response_data)
        
        # If approved, return success message
        if approval_request.approved:
            return JSONResponse(content={
                "success": True,
                "message": "Post has been successfully posted to LinkedIn!",
                "posted_to_linkedin": final_state.posted_to_linkedin
            })
        
        # If rejected
        return JSONResponse(content={
            "success": False,
            "message": "Post generation cancelled by user."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
