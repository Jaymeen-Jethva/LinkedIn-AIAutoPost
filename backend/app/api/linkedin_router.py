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
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.clients.db import get_db
from app.services.user_service import UserService

load_dotenv()

router = APIRouter()

# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', "http://localhost:8000/linkedin/callback")
LINKEDIN_SCOPE = "openid profile w_member_social email"


@router.get("/status")
async def linkedin_status(user_id: str = Query(None), db: AsyncSession = Depends(get_db)):
    """Check if user is connected to LinkedIn"""
    if not user_id:
        return JSONResponse(content={"connected": False, "message": "No user ID provided"})

    user_service = UserService(db)
    credential = await user_service.get_credentials(user_id)
    
    if credential:
        return JSONResponse(content={
            "connected": True,
            "person_id": credential.linkedin_person_id,
            "message": "Connected to LinkedIn"
        })
    
    return JSONResponse(content={
        "connected": False,
        "message": "Not connected to LinkedIn"
    })


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
async def linkedin_callback(
    code: str = None, 
    error: str = None, 
    error_description: str = None,
    db: AsyncSession = Depends(get_db)
):
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
        full_name = user_data.get("name")
        email = user_data.get("email")
        picture = user_data.get("picture")
        
        # DB Persistence Logic
        user_service = UserService(db)
        
        # Check if user exists via LinkedIn ID
        existing_user = await user_service.get_user_by_linkedin_id(person_id)
        
        if existing_user:
            # Update credentials
            await user_service.update_linkedin_credentials(existing_user.id, access_token, expires_in)
            user_id = existing_user.id
        else:
            # Create new user
            new_user = await user_service.create_user_with_linkedin(
                linkedin_person_id=person_id,
                access_token=access_token,
                expires_in=expires_in,
                full_name=full_name,
                email=email,
                avatar_url=picture
            )
            user_id = new_user.id

        # Redirect back to frontend with user_id
        return RedirectResponse(url=f"{FRONTEND_URL}/?linkedin_connected=true&user_id={user_id}")
        
    except requests.exceptions.RequestException as e:
        return RedirectResponse(url=f"{FRONTEND_URL}/?linkedin_error=Token exchange failed: {str(e)}")
    except Exception as e:
        return RedirectResponse(url=f"{FRONTEND_URL}/?linkedin_error={str(e)}")


@router.post("/disconnect")
async def linkedin_disconnect(user_id: str = Query(...)):
    """Disconnect LinkedIn (Placeholder - requires auth impl)"""
    # Todo: Implement delete credential logic in UserService
    return JSONResponse(content={
        "success": True,
        "message": "Disconnected (Note: Token remains in DB until implemented)"
    })
