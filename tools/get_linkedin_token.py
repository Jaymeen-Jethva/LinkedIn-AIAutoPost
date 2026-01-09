import os
import secrets
import webbrowser
import uvicorn
import requests
from fastapi import FastAPI, Request
from urllib.parse import urlencode

# --- CONFIGURATION ---
# User will be prompted to enter these if not found in env
CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "openid profile w_member_social email" 
# 'openid' & 'profile' & 'email' -> for Sign In with LinkedIn (OpenID Connect)
# 'w_member_social' -> for Sharing on LinkedIn

app = FastAPI()

@app.get("/")
def home():
    return "LinkedIn Auth Tool Running. Please return to your terminal."

@app.get("/callback")
def callback(code: str = None, error: str = None, error_description: str = None):
    if error:
        return f"Error: {error} - {error_description}"
    
    if not code:
        return "No code received."

    # Exchange code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(token_url, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        access_token = data.get("access_token")
        
        # Now fetch the user's profile to get the URN (Person ID)
        # Using the UserInfo endpoint for OpenID Connect
        userinfo_url = "https://api.linkedin.com/v2/userinfo"
        user_headers = {"Authorization": f"Bearer {access_token}"}
        
        user_response = requests.get(userinfo_url, headers=user_headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        person_urn = user_data.get("sub") # 'sub' is the unique Subject (Person ID)
        
        print("\n" + "="*50)
        print("SUCCESS! HERE ARE YOUR CREDENTIALS:")
        print("="*50)
        print(f"\nLINKEDIN_ACCESS_TOKEN={access_token}")
        print(f"LINKEDIN_PERSON_ID={person_urn}")
        print("\n" + "="*50)
        print("Copy these lines into your .env file.")
        
        # Shutdown server (simple way)
        os._exit(0)
        
        return "Authentication Successful! Check your terminal for the Access Token and Person ID."
        
    except Exception as e:
        return f"Error during token exchange: {str(e)}"

def start_auth_flow():
    global CLIENT_ID, CLIENT_SECRET
    
    print("\n--- LinkedIn Token Generator ---\n")
    if not CLIENT_ID:
        CLIENT_ID = input("Enter your LinkedIn Client ID: ").strip()
    if not CLIENT_SECRET:
        CLIENT_SECRET = input("Enter your LinkedIn Client Secret: ").strip()
        
    state = secrets.token_hex(16)
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": SCOPE,
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    
    print(f"\nOpening browser to: {auth_url}")
    webbrowser.open(auth_url)
    
    print("\nWaiting for callback on http://localhost:8080/callback ...")
    uvicorn.run(app, host="localhost", port=8080, log_level="warning")

if __name__ == "__main__":
    start_auth_flow()
