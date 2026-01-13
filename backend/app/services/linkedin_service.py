import requests
import json
import os
from typing import Optional, Dict, Any
from app.clients.token_client import load_token

class LinkedInAPI:
    """LinkedIn API integration for posting content"""
    
    def __init__(self):
        self.base_url = 'https://api.linkedin.com/v2'
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from token.json"""
        token_data = load_token()
        if token_data:
            self.access_token = token_data.get('access_token')
            self.person_id = token_data.get('person_id')
        else:
            self.access_token = None
            self.person_id = None
    
    def reload_token(self):
        """Reload token from file - useful after OAuth callback"""
        self._load_credentials()
        
    def is_configured(self) -> bool:
        """Check if LinkedIn API is properly configured"""
        return bool(self.access_token and self.person_id)
    
    def post_text_content(self, content: str, hashtags: list = None) -> Dict[str, Any]:
        """Post text content to LinkedIn"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "LinkedIn API not configured. Please add LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID to your environment variables."
            }
        
        # Combine content and hashtags
        full_content = content
        if hashtags:
            full_content += "\n\n" + " ".join(hashtags)
        
        payload = {
            "author": f"urn:li:person:{self.person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": full_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/ugcPosts',
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "post_id": response.json().get('id'),
                    "message": "Post successfully published to LinkedIn!"
                }
            else:
                return {
                    "success": False,
                    "error": f"LinkedIn API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to post to LinkedIn: {str(e)}"
            }
    
    def post_content_with_image(self, content: str, image_path: str, hashtags: list = None) -> Dict[str, Any]:
        """Post content with image to LinkedIn"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "LinkedIn API not configured. Please add LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID to your environment variables."
            }
        
        try:
            # Step 1: Upload image
            image_upload_result = self._upload_image(image_path)
            if not image_upload_result.get("success"):
                return image_upload_result
            
            # Step 2: Create post with image
            full_content = content
            if hashtags:
                full_content += "\n\n" + " ".join(hashtags)
            
            payload = {
                "author": f"urn:li:person:{self.person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": full_content
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": "Generated image for LinkedIn post"
                                },
                                "media": image_upload_result["asset_urn"],
                                "title": {
                                    "text": "LinkedIn Post Image"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            response = requests.post(
                f'{self.base_url}/ugcPosts',
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "post_id": response.json().get('id'),
                    "message": "Post with image successfully published to LinkedIn!"
                }
            else:
                return {
                    "success": False,
                    "error": f"LinkedIn API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to post to LinkedIn: {str(e)}"
            }
    
    def _upload_image(self, image_path: str) -> Dict[str, Any]:
        """Upload image to LinkedIn and return asset URN"""
        try:
            # Step 1: Register upload
            register_payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{self.person_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            register_response = requests.post(
                f'{self.base_url}/assets?action=registerUpload',
                headers=headers,
                data=json.dumps(register_payload)
            )
            
            if register_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to register image upload: {register_response.status_code}"
                }
            
            register_data = register_response.json()
            upload_mechanism = register_data['value']['uploadMechanism']
            upload_url = upload_mechanism['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = register_data['value']['asset']
            
            # Step 2: Upload the actual image
            with open(image_path, 'rb') as image_file:
                upload_headers = {
                    'Authorization': f'Bearer {self.access_token}'
                }
                
                upload_response = requests.post(
                    upload_url,
                    headers=upload_headers,
                    files={'file': image_file}
                )
                
                if upload_response.status_code != 201:
                    return {
                        "success": False,
                        "error": f"Failed to upload image: {upload_response.status_code}"
                    }
            
            return {
                "success": True,
                "asset_urn": asset_urn
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Image upload failed: {str(e)}"
            }
    
    def get_profile_info(self) -> Dict[str, Any]:
        """Get basic profile information"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "LinkedIn API not configured"
            }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f'{self.base_url}/people/(id:{self.person_id})',
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "profile": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get profile: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Profile fetch failed: {str(e)}"
            }


# Global LinkedIn API instance
linkedin_api = LinkedInAPI()