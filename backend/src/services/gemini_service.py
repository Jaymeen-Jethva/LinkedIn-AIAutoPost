import json
import logging
import os
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.tools.tavily_tool import tavily_search, create_search_enhanced_prompt

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retry decorator for Gemini API calls - handles transient failures
def gemini_retry():
    """Retry decorator with exponential backoff for Gemini API calls"""
    return retry(
        stop=stop_after_attempt(3),  # Max 3 attempts
        wait=wait_exponential(multiplier=1, min=2, max=10),  # 2s, 4s, 8s backoff
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        before_sleep=lambda retry_state: logger.warning(
            f"Gemini API call failed, retrying in {retry_state.next_action.sleep} seconds... "
            f"(Attempt {retry_state.attempt_number}/3)"
        ),
        reraise=True
    )

# IMPORTANT: KEEP THIS COMMENT
# Follow these instructions when using this blueprint:
# - Note that the newest Gemini model series is "gemini-2.5-flash" or gemini-2.5-pro"
#   - do not change this unless explicitly requested by the user
# - Sometimes the google genai SDK has occasional type errors. You might need to run to validate, at time.
# The SDK was recently renamed from google-generativeai to google-genai. This file reflects the new name and the new APIs.

# This API key is from Gemini Developer API Key, not vertex AI API Key
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class LinkedInPost(BaseModel):
    content: str
    hashtags: list[str]
    image_prompt: Optional[str] = None  # Make image_prompt optional
    post_type: str  # "ai_news" or "personal_milestone"


@gemini_retry()
def _generate_with_retry(model: str, user_prompt: str, system_prompt: str, response_schema=None):
    """Internal function that wraps Gemini API calls with retry logic"""
    logger.info(f"Calling Gemini model: {model}")
    return client.models.generate_content(
        model=model,
        contents=[
            types.Content(role="user", parts=[types.Part(text=user_prompt)])
        ],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
    )


def generate_linkedin_post(topic: str, post_type: str, user_preferences: dict = {}, include_image: bool = True, use_web_search: bool = True) -> LinkedInPost:
    """Generate a LinkedIn post based on topic and type using Gemini AI with optional web search"""

    # Perform web search if enabled and available
    search_results = []
    search_context = ""

    if use_web_search and tavily_search.is_available():
        try:
            logging.info(f"Performing web search for topic: {topic}")

            if post_type == "ai_news":
                # Search for AI and technology news
                search_results = tavily_search.search_ai_news(topic)
            else:
                # Search for technical information and best practices
                search_results = tavily_search.search_technical_info(topic)

            if search_results:
                search_context = tavily_search.format_search_results_for_ai(search_results)
                logging.info(f"Web search completed. Found {len(search_results)} results.")
            else:
                logging.info("Web search completed but no relevant results found.")

        except Exception as e:
            logging.error(f"Web search failed: {e}")
            search_context = "Web search unavailable - proceeding with AI knowledge only."

    # Create base prompts
    if post_type == "ai_news":
        base_system_prompt = (
            "You are a LinkedIn content creator specializing in AI and technology news. "
            "Create an engaging LinkedIn post about the given topic. "
            "The post should be professional, informative, and include relevant hashtags. "
            "Keep the post content between 150-300 words and make it engaging for a professional audience."
        )
        if include_image:
            base_system_prompt += " Also provide a detailed image prompt for generating a relevant visual."
        base_user_prompt = f"Create a LinkedIn post about this AI/tech topic: {topic}"
    else:  # personal_milestone
        base_system_prompt = (
            "You are a LinkedIn content creator helping people share personal and professional milestones. "
            "Create an inspiring and authentic LinkedIn post about the given personal achievement or milestone. "
            "The post should be motivational, relatable, and include relevant hashtags. "
            "Keep the post content between 100-250 words and make it personal yet professional."
        )
        if include_image:
            base_system_prompt += " Also provide a detailed image prompt for generating a relevant visual."
        base_user_prompt = f"Create a LinkedIn post about this personal milestone: {topic}"

    # Enhance prompts with web search results if available
    if search_context and search_results:
        system_prompt = create_search_enhanced_prompt(base_system_prompt, search_context, topic)
        user_prompt = f"{base_user_prompt}\n\nWeb search context available for enhanced accuracy."
    else:
        system_prompt = base_system_prompt
        user_prompt = base_user_prompt

    if user_preferences:
        user_prompt += f"\n\nUser preferences: {user_preferences}"

    try:
        # Conditionally build the response schema
        response_schema_parts = {
            "content": {"type": "string"},
            "hashtags": {"type": "array", "items": {"type": "string"}},
            "post_type": {"type": "string"}
        }
        if include_image:
            response_schema_parts["image_prompt"] = {"type": "string"}

        response_schema = types.Schema(
            type=types.Type.OBJECT,
            properties=response_schema_parts
        )

        response = _generate_with_retry(
            model="gemini-2.5-flash",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            response_schema=response_schema
        )

        raw_json = response.text
        logging.info(f"Raw JSON from Gemini: {raw_json}")

        if raw_json:
            data = json.loads(raw_json)
            # Manually create LinkedInPost, handling optional image_prompt
            post = LinkedInPost(
                content=data.get("content"),
                hashtags=data.get("hashtags", []),
                image_prompt=data.get("image_prompt"),
                post_type=data.get("post_type")
            )

            # Add metadata about web search usage
            if search_results:
                logging.info(f"Post generated with web search enhancement. Used {len(search_results)} search results.")

            return post
        else:
            raise ValueError("Empty response from Gemini model")

    except Exception as e:
        raise Exception(f"Failed to generate LinkedIn post: {e}")


def generate_linkedin_post_with_search(topic: str, post_type: str, user_preferences: dict = {}, include_image: bool = True) -> tuple[LinkedInPost, List[Dict[str, Any]]]:
    """
    Generate a LinkedIn post with web search results

    Returns:
        tuple: (LinkedInPost, search_results_list)
    """
    # Always perform web search for this function
    search_results = []

    if tavily_search.is_available():
        try:
            if post_type == "ai_news":
                search_results = tavily_search.search_ai_news(topic)
            else:
                search_results = tavily_search.search_technical_info(topic)
        except Exception as e:
            logging.error(f"Web search failed: {e}")

    # Generate post using search results
    post = generate_linkedin_post(topic, post_type, user_preferences, include_image, use_web_search=True)

    return post, search_results


def revise_linkedin_post(original_post: LinkedInPost, feedback: str) -> LinkedInPost:
    """Revise a LinkedIn post based on user feedback"""
    
    system_prompt = (
        "You are helping revise a LinkedIn post based on user feedback. "
        "Take the original post and the user's feedback to create an improved version. "
        "Maintain the professional tone and structure while incorporating the requested changes."
    )
    
    user_prompt = f"""
    Original post content: {original_post.content}
    Original hashtags: {', '.join(original_post.hashtags)}
    Original image prompt: {original_post.image_prompt}
    Post type: {original_post.post_type}
    
    User feedback: {feedback}
    
    Please revise the post based on this feedback.
    """

    try:
        response = _generate_with_retry(
            model="gemini-2.5-pro",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            response_schema=LinkedInPost
        )

        raw_json = response.text
        if raw_json:
            data = json.loads(raw_json)
            return LinkedInPost(**data)
        else:
            raise ValueError("Empty response from Gemini model")

    except Exception as e:
        raise Exception(f"Failed to revise LinkedIn post: {e}")


def generate_image_with_gemini(prompt: str, image_path: str) -> bool:
    """Generate an image using Gemini's image generation capability"""
    try:
        # List available models for debugging (only on first failure)
        IMAGE_MODEL = "gemini-2.5-flash-image"  # Updated model name
        
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']))

        if not response.candidates:
            return False

        content = response.candidates[0].content
        if not content or not content.parts:
            return False

        for part in content.parts:
            if part.inline_data and part.inline_data.data:
                with open(image_path, 'wb') as f:
                    f.write(part.inline_data.data)
                print(f"Image generated and saved as {image_path}")
                return True
        
        return False
    except Exception as e:
        print(f"Failed to generate image with Gemini: {e}")
        # List available image generation models for debugging
        try:
            print("Available Gemini models supporting image generation:")
            for model in client.models.list():
                model_name = model.name if hasattr(model, 'name') else str(model)
                if 'image' in model_name.lower():
                    print(f"  - {model_name}")
        except Exception as list_error:
            print(f"Could not list models: {list_error}")
        return False


def generate_image_with_pollinations(prompt: str, image_path: str) -> bool:
    """
    Generate an image using Pollinations.ai (fallback)
    Pollinations is a free, URL-based image generation service.
    """
    import requests
    import time
    import logging
    
    try:
        # Construct Pollinations URL
        # We encode the prompt and add detailed parameters for better quality
        # Using flux model which is excellent for photorealism
        encoded_prompt = requests.utils.quote(f"{prompt}, high quality, detailed, 8k, photorealistic")
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&seed={int(time.time())}"
        
        logging.info(f"Generating image with Pollinations: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            logging.info(f"Image generated with Pollinations and saved to {image_path}")
            return True
        else:
            logging.error(f"Pollinations API error: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"Failed to generate image with Pollinations: {e}")
        return False
