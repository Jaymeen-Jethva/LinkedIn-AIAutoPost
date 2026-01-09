"""
Token Storage Module for LinkedIn OAuth

Handles saving and loading LinkedIn access tokens from a JSON file.
"""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

TOKEN_FILE = "token.json"


def save_token(access_token: str, person_id: str, expires_in: int = None) -> bool:
    """
    Save OAuth token data to token.json
    
    Args:
        access_token: LinkedIn access token
        person_id: LinkedIn user person ID (sub from userinfo)
        expires_in: Token validity in seconds (optional)
    
    Returns:
        bool: True if saved successfully
    """
    try:
        token_data = {
            "access_token": access_token,
            "person_id": person_id,
            "created_at": datetime.now().isoformat(),
        }
        
        if expires_in:
            token_data["expires_in"] = expires_in
        
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving token: {e}")
        return False


def load_token() -> Optional[Dict[str, Any]]:
    """
    Load token data from token.json
    
    Returns:
        dict with token data or None if not found
    """
    try:
        if not os.path.exists(TOKEN_FILE):
            return None
        
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading token: {e}")
        return None


def is_token_valid() -> bool:
    """
    Check if a valid token exists
    
    Returns:
        bool: True if token exists (no expiration check as per requirements)
    """
    token_data = load_token()
    if not token_data:
        return False
    
    # Check if required fields exist
    return bool(token_data.get("access_token") and token_data.get("person_id"))


def delete_token() -> bool:
    """
    Delete the token file
    
    Returns:
        bool: True if deleted or didn't exist
    """
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        return True
    except Exception as e:
        print(f"Error deleting token: {e}")
        return False


def get_token_status() -> Dict[str, Any]:
    """
    Get current token status for API response
    
    Returns:
        dict with connection status info
    """
    token_data = load_token()
    
    if not token_data or not is_token_valid():
        return {
            "connected": False,
            "message": "Not connected to LinkedIn"
        }
    
    return {
        "connected": True,
        "person_id": token_data.get("person_id"),
        "created_at": token_data.get("created_at"),
        "message": "Connected to LinkedIn"
    }
