"""
LinkedIn OAuth Router

Handles LinkedIn OAuth 2.0 authentication flow:
- /status - Check connection status
- /connect - Initiate OAuth flow
- /callback - Handle OAuth callback
- /disconnect - Remove stored tokens
"""
import os
import secrets
import requests
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv

from app.models.linkedin_models import (
    LinkedInConnectResponse,
    LinkedInStatusResponse,
    LinkedInDisconnectResponse
)
from app.clients.token_client import (
    save_token,
    delete_token,
    get_token_status
)
from app.services.linkedin_service import linkedin_api

load_dotenv()

router = APIRouter()

# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = "http://localhost:8000/linkedin/callback"
LINKEDIN_SCOPE = "openid profile w_member_social email"


@router.get("/status")
async def linkedin_status():
    """Check if user is connected to LinkedIn"""
    return JSONResponse(content=get_token_status())


@router.post("/connect")
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


@router.get("/callback")
async def linkedin_callback(code: str = None, error: str = None, error_description: str = None):
    """Handle OAuth callback from LinkedIn"""
    # Frontend URL for redirects
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}/?linkedin_error={error_description or error}")
    
    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}/?linkedin_error=No authorization code received")
    
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
        
        # Redirect back to frontend with success
        return RedirectResponse(url=f"{FRONTEND_URL}/?linkedin_connected=true")
        
    except requests.exceptions.RequestException as e:
        return RedirectResponse(url=f"{FRONTEND_URL}/?linkedin_error=Token exchange failed: {str(e)}")
    except Exception as e:
        return RedirectResponse(url=f"{FRONTEND_URL}/?linkedin_error={str(e)}")


@router.post("/disconnect")
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
