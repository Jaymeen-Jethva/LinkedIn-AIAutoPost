import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configure API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables")
    exit(1)

client = genai.Client(api_key=api_key)

print("Listing available Gemini models...")
try:
    models = client.models.list()
    found_image_model = False
    
    for m in models:
        print(f"- {m.name}: {getattr(m, 'supported_generation_methods', 'Unknown')}")
        if 'image' in m.name.lower():
            found_image_model = True
            print(f"  >>> POTENTIAL IMAGE MODEL FOUND: {m.name}")
            
    if not found_image_model:
        print("\nNo obvious image generation models found in the list.")

        
except Exception as e:
    print(f"Error listing models: {e}")
