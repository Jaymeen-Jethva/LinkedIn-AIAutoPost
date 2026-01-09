import os
import json
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict
from linkedin_workflow import linkedin_workflow, WorkflowState
import uvicorn
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="LinkedIn Post Automation", description="AI-powered LinkedIn post generation with approval workflow")

# Create directories if they don't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("generated_images", exist_ok=True)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# Try to mount static files, create empty directory if it doesn't exist
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    pass

# In-memory storage for workflow states (in production, use a proper database)
workflow_sessions = {}

class PostRequest(BaseModel):
    topic: str
    post_type: str  # "ai_news" or "personal_milestone"
    user_preferences: Optional[Dict] = {}
    include_image: bool = True  # New field for image preference

class ApprovalRequest(BaseModel):
    session_id: str
    approved: bool
    feedback: Optional[str] = ""


# Input validation constants
MIN_TOPIC_LENGTH = 10
MAX_TOPIC_LENGTH = 500
ALLOWED_POST_TYPES = ["ai_news", "personal_milestone"]
# Characters that might cause issues in prompts
DANGEROUS_CHARS_PATTERN = r'[<>{}|\\^`]'


def validate_topic(topic: str) -> tuple[bool, str]:
    """
    Validate topic input for length and dangerous characters.
    Returns (is_valid, error_message)
    """
    import re
    
    # Check if empty
    if not topic or not topic.strip():
        return False, "Topic cannot be empty"
    
    # Check minimum length
    if len(topic.strip()) < MIN_TOPIC_LENGTH:
        return False, f"Topic must be at least {MIN_TOPIC_LENGTH} characters long"
    
    # Check maximum length
    if len(topic) > MAX_TOPIC_LENGTH:
        return False, f"Topic must not exceed {MAX_TOPIC_LENGTH} characters"
    
    # Check for dangerous characters
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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage with topic input form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-post")
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
        import uuid
        session_id = str(uuid.uuid4())
        
        # Run the workflow until user approval is needed
        result_state = linkedin_workflow.run_workflow(
            topic=post_request.topic.strip(),  # Clean input
            post_type=post_request.post_type,
            user_preferences=post_request.user_preferences,
            include_image=post_request.include_image
        )
        
        # Store the state for later continuation
        workflow_sessions[session_id] = result_state
        
        if result_state.error:
            raise HTTPException(status_code=500, detail=result_state.error)
        
        # Return the generated content for user review
        response_data = {
            "session_id": session_id,
            "content": result_state.generated_post.content if result_state.generated_post else "",
            "hashtags": result_state.generated_post.hashtags if result_state.generated_post else [],
            "image_path": result_state.image_path,
            "image_prompt": result_state.generated_post.image_prompt if result_state.generated_post else "",
            "post_type": result_state.post_type
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve-post")
async def approve_post(approval_request: ApprovalRequest):
    """Handle user approval or feedback for the generated post"""
    try:
        session_id = approval_request.session_id
        
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        current_state = workflow_sessions[session_id]
        
        # Continue the workflow with user decision
        final_state = linkedin_workflow.continue_workflow_with_approval(
            state=current_state,
            approved=approval_request.approved,
            feedback=approval_request.feedback or ""
        )
        
        # Update the stored state
        workflow_sessions[session_id] = final_state
        
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

@app.get("/preview/{session_id}", response_class=HTMLResponse)
async def preview_post(session_id: str, request: Request):
    """Preview page for generated post"""
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = workflow_sessions[session_id]
    return templates.TemplateResponse("preview.html", {
        "request": request,
        "session_id": session_id,
        "state": state
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "LinkedIn automation service is running"}

# Mount generated images directory
try:
    app.mount("/images", StaticFiles(directory="generated_images"), name="images")
except RuntimeError:
    pass

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5000, 
        reload=True,
        log_level="info"
    )
