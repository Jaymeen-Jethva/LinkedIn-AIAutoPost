import requests
import json
from typing import Optional, Dict, Any


class LinkedInAPI:
    """LinkedIn API integration for posting content (Stateless)"""
    
    def __init__(self):
        self.base_url = 'https://api.linkedin.com/v2'

    def post_text_content(self, text: str, access_token: str, person_id: str) -> Optional[str]:
        """
        Post text-only content to LinkedIn
        Returns the URN of the created post or None if failed
        """
        if not access_token or not person_id:
            print("Error: Access token or Person ID missing")
            return None
            
        url = f"{self.base_url}/ugcPosts"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            urn = data.get("id")
            print(f"✅ Successfully posted text to LinkedIn! URN: {urn}")
            return urn
        except Exception as e:
            print(f"Error posting text content: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None

    def post_image_content(self, text: str, image_path: str, access_token: str, person_id: str) -> Optional[str]:
        """
        Post content with image to LinkedIn
        1. Register upload
        2. Upload image
        3. Create post referencing image
        """
        if not access_token or not person_id:
            return None
            
        # Step 1: Register Upload
        asset_urn, upload_url = self._register_upload(access_token, person_id)
        if not asset_urn or not upload_url:
            return None
            
        # Step 2: Upload Image Binary
        if not self._upload_image_binary(image_path, upload_url, access_token):
            return None
            
        # Step 3: Create Post
        return self._create_image_post(text, asset_urn, access_token, person_id)

    def _register_upload(self, access_token: str, person_id: str) -> tuple[Optional[str], Optional[str]]:
        """Register the image upload with LinkedIn to get upload URL and URN"""
        url = f"{self.base_url}/assets?action=registerUpload"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{person_id}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract upload URL and Asset URN
            upload_mechanism = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']
            upload_url = upload_mechanism['uploadUrl']
            asset_urn = data['value']['asset']
            
            return asset_urn, upload_url
        except Exception as e:
            print(f"Error registering upload: {e}")
            return None, None

    def _upload_image_binary(self, image_path: str, upload_url: str, access_token: str) -> bool:
        """Upload the actual image file to the URL provided by LinkedIn"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream"
        }
        
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
                
            response = requests.put(upload_url, headers=headers, data=image_data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error uploading image binary: {e}")
            return False

    def _create_image_post(self, text: str, asset_urn: str, access_token: str, person_id: str) -> Optional[str]:
        """Final step: Create the post referencing the uploaded image asset"""
        url = f"{self.base_url}/ugcPosts"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Generated Image"
                            },
                            "media": asset_urn,
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
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            urn = data.get("id")
            print(f"✅ Successfully posted image content! URN: {urn}")
            return urn
        except Exception as e:
            print(f"Error creating image post: {e}")
            return None


# Global Stateless Instance
linkedin_api = LinkedInAPI()