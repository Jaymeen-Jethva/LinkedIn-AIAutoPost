"""
Post Generation Router

Handles LinkedIn post generation workflow:
- /generate-post - Generate a new post
- /approve-post - Approve or request revision
"""
import re
import uuid
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.services.post_service import PostService
from app.clients.db import get_db

router = APIRouter()

# In-memory storage for active workflow sessions (still needed for session persistence across requests)
# In a real scaled app, this state should be serialized to DB or Redis.
workflow_sessions = {}

# Characters that might cause issues in prompts
DANGEROUS_CHARS_PATTERN = r'[<>{}|\\^`]'


def validate_topic(topic: str) -> tuple[bool, str]:
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
    if post_type not in ALLOWED_POST_TYPES:
        return False, f"Invalid post type. Must be one of: {', '.join(ALLOWED_POST_TYPES)}"
    return True, ""


@router.post("/generate-post")
async def generate_post(
    post_request: PostRequest, 
    user_id: str = Query(..., description="User ID associated with the request"),
    db: AsyncSession = Depends(get_db)
):
    """Generate a LinkedIn post based on user input"""
    # Validate input
    is_valid, error_msg = validate_topic(post_request.topic)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    is_valid, error_msg = validate_post_type(post_request.post_type)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        session_id = str(uuid.uuid4())
        
        # 1. Create DB Post Entry (Draft)
        post_service = PostService(db)
        await post_service.create_draft_post(
            user_id=user_id,
            session_id=session_id,
            topic=post_request.topic,
            post_type=post_request.post_type
        )
        
        # 2. Initialize Workflow
        workflow_instance = LinkedInWorkflow(use_multi_agent=post_request.use_multi_agent)
        
        # 3. Run Workflow (Step 1: Generation)
        # Using async version now
        result_state = await workflow_instance.run_workflow_async(
            topic=post_request.topic.strip(),
            post_type=post_request.post_type,
            user_preferences=post_request.user_preferences,
            include_image=post_request.include_image
        )
        
        # 4. Update DB with generated content
        if result_state.generated_post:
            await post_service.update_post_content(
                session_id=session_id,
                content=result_state.generated_post.content,
                image_path=result_state.image_path,
                image_prompt=result_state.generated_post.image_prompt
            )

        # Store session in memory for approval step
        workflow_sessions[session_id] = {
            "state": result_state,
            "workflow": workflow_instance,
            "user_id": user_id 
        }
        
        if result_state.error:
            raise HTTPException(status_code=500, detail=result_state.error)
        
        return JSONResponse(content={
            "session_id": session_id,
            "content": result_state.generated_post.content if result_state.generated_post else "",
            "hashtags": result_state.generated_post.hashtags if result_state.generated_post else [],
            "image_path": result_state.image_path,
            "image_prompt": result_state.generated_post.image_prompt if result_state.generated_post else "",
            "post_type": result_state.post_type,
            "multi_agent_used": post_request.use_multi_agent
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve-post")
async def approve_post(
    approval_request: ApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """Handle user approval or feedback"""
    try:
        session_id = approval_request.session_id
        
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = workflow_sessions[session_id]
        current_state = session_data["state"]
        workflow_instance = session_data["workflow"]
        user_id = session_data["user_id"]
        
        # Inject DB session and UserID into state for the workflow to use
        current_state.user_id = user_id
        current_state.db_session = db
        
        # Continue Workflow
        final_state = await workflow_instance.continue_workflow_with_approval(
            state=current_state,
            approved=approval_request.approved,
            feedback=approval_request.feedback or ""
        )
        
        # Update session state
        workflow_sessions[session_id]["state"] = final_state
        
        if final_state.error:
            raise HTTPException(status_code=500, detail=final_state.error)
        
        # DB Updates based on outcome
        post_service = PostService(db)
        
        # If Revised
        if approval_request.feedback and not approval_request.approved:
            if final_state.generated_post:
                await post_service.update_post_content(
                    session_id=session_id,
                    content=final_state.generated_post.content
                )
            
            return JSONResponse(content={
                "session_id": session_id,
                "content": final_state.generated_post.content,
                "hashtags": final_state.generated_post.hashtags,
                "image_path": final_state.image_path,
                "post_type": final_state.post_type,
                "revised": True
            })
        
        # If Posted
        if approval_request.approved and final_state.posted_to_linkedin:
            # Ideally get URN from state if available, but for now we mark as posted
            await post_service.mark_as_posted(session_id, "urn:li:share:example")
            
            return JSONResponse(content={
                "success": True,
                "message": "Post has been successfully posted to LinkedIn!",
                "posted_to_linkedin": True
            })
        
        return JSONResponse(content={
            "success": False,
            "message": "Post generation cancelled by user."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
