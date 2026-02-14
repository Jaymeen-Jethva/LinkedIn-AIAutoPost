"""
LinkedIn OAuth Service

Handles LinkedIn OAuth 2.0 authentication following Single Responsibility Principle.
Separated from controllers for better testability and reusability.
"""
import requests
import secrets
from urllib.parse import urlencode
from typing import Dict, Tuple
from src.framework import settings, ExternalServiceError, ValidationError


class LinkedInOAuthService:
    """Service for LinkedIn OAuth 2.0 authentication"""
    
    def __init__(self):
        """Initialize OAuth service with configuration from settings"""
        if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
            raise ValidationError(
                "LinkedIn OAuth not configured. Add LINKEDIN_CLIENT_ID and "
                "LINKEDIN_CLIENT_SECRET to your .env file."
            )
        
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = settings.LINKEDIN_REDIRECT_URI
        self.oauth_url = settings.LINKEDIN_OAUTH_URL
        self.token_url = settings.LINKEDIN_TOKEN_URL
        self.api_base = settings.LINKEDIN_API_BASE
        self.scope = "openid profile w_member_social email"
    
    def generate_authorization_url(self) -> Tuple[str, str]:
        """
        Generate LinkedIn OAuth authorization URL with CSRF protection.
        
        Returns:
            Tuple of (authorization_url, state_token)
            
        Raises:
            ValidationError: If OAuth is not configured
        """
        # Generate state for CSRF protection
        state = secrets.token_hex(16)
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": self.scope,
        }
        
        auth_url = f"{self.oauth_url}?{urlencode(params)}"
        
        return auth_url, state
    
    def exchange_code_for_token(self, code: str) -> Dict[str, any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: LinkedIn authorization code from OAuth callback
            
        Returns:
            Dictionary with access_token and expires_in
            
        Raises:
            ExternalServiceError: If token exchange fails
        """
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = requests.post(self.token_url, data=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            access_token = data.get("access_token")
            expires_in = data.get("expires_in")
            
            if not access_token:
                raise ExternalServiceError(
                    "LinkedIn",
                    "No access token in response"
                )
            
            return {
                "access_token": access_token,
                "expires_in": expires_in
            }
            
        except requests.exceptions.Timeout:
            raise ExternalServiceError("LinkedIn", "Request timed out during token exchange")
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise ExternalServiceError("LinkedIn", f"Token exchange failed - {error_msg}")
        except requests.exceptions.RequestException as e:
            raise ExternalServiceError("LinkedIn", f"Token exchange failed - {str(e)}")
    
    def get_user_info(self, access_token: str) -> Dict[str, any]:
        """
        Fetch LinkedIn user profile information.
        
        Args:
            access_token: LinkedIn access token
            
        Returns:
            Dictionary with user profile data (sub, name, email, picture)
            
        Raises:
            ExternalServiceError: If API call fails
        """
        userinfo_url = f"{self.api_base}/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(userinfo_url, headers=headers, timeout=10)
            response.raise_for_status()
            user_data = response.json()
            
            return {
                "person_id": user_data.get("sub"),  # Unique LinkedIn person ID
                "full_name": user_data.get("name"),
                "email": user_data.get("email"),
                "avatar_url": user_data.get("picture")
            }
            
        except requests.exceptions.Timeout:
            raise ExternalServiceError("LinkedIn", "Request timed out while fetching user info")
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise ExternalServiceError("LinkedIn", f"Failed to fetch user info - {error_msg}")
        except requests.exceptions.RequestException as e:
            raise ExternalServiceError("LinkedIn", f"Failed to fetch user info - {str(e)}")
