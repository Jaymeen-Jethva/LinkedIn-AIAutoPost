import os
import json
import secrets
import requests
from urllib.parse import urlencode
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict
from linkedin_workflow import linkedin_workflow, WorkflowState
from linkedin_api import linkedin_api
from token_storage import save_token, load_token, is_token_valid, delete_token, get_token_status
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

# ================================================
# LinkedIn OAuth Endpoints
# ================================================

# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = "http://localhost:8000/linkedin/callback"
LINKEDIN_SCOPE = "openid profile w_member_social email"


@app.get("/linkedin/status")
async def linkedin_status():
    """Check if user is connected to LinkedIn"""
    return JSONResponse(content=get_token_status())


@app.post("/linkedin/connect")
async def linkedin_connect():
    """Generate LinkedIn authorization URL and return it"""
    if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="LinkedIn OAuth not configured. Please add LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET to your .env file."
        )
    
    # Generate state for CSRF protection
    state = secrets.token_hex(16)
    
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "state": state,
        "scope": LINKEDIN_SCOPE,
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    
    return JSONResponse(content={
        "authorization_url": auth_url,
        "message": "Redirect user to this URL to authorize"
    })


@app.get("/linkedin/callback")
async def linkedin_callback(code: str = None, error: str = None, error_description: str = None):
    """Handle OAuth callback from LinkedIn"""
    if error:
        # Redirect back to home with error
        return RedirectResponse(url=f"/?linkedin_error={error_description or error}")
    
    if not code:
        return RedirectResponse(url="/?linkedin_error=No authorization code received")
    
    # Exchange code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(token_url, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        access_token = data.get("access_token")
        expires_in = data.get("expires_in")
        
        # Fetch user's profile to get the URN (Person ID)
        userinfo_url = "https://api.linkedin.com/v2/userinfo"
        user_headers = {"Authorization": f"Bearer {access_token}"}
        
        user_response = requests.get(userinfo_url, headers=user_headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        person_id = user_data.get("sub")  # 'sub' is the unique Subject (Person ID)
        
        # Save token to file
        save_token(access_token, person_id, expires_in)
        
        # Reload token in linkedin_api instance
        linkedin_api.reload_token()
        
        # Redirect back to home with success
        return RedirectResponse(url="/?linkedin_connected=true")
        
    except requests.exceptions.RequestException as e:
        return RedirectResponse(url=f"/?linkedin_error=Token exchange failed: {str(e)}")
    except Exception as e:
        return RedirectResponse(url=f"/?linkedin_error={str(e)}")


@app.post("/linkedin/disconnect")
async def linkedin_disconnect():
    """Disconnect LinkedIn by deleting stored token"""
    success = delete_token()
    
    # Reload linkedin_api to clear credentials
    linkedin_api.reload_token()
    
    if success:
        return JSONResponse(content={
            "success": True,
            "message": "Successfully disconnected from LinkedIn"
        })
    else:
        raise HTTPException(status_code=500, detail="Failed to disconnect")


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
