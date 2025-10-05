import json
import logging
import os
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
from tavily_search import tavily_search, create_search_enhanced_prompt

load_dotenv()

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
    image_prompt: str
    post_type: str  # "ai_news" or "personal_milestone"


def generate_linkedin_post(topic: str, post_type: str, user_preferences: dict = {}, use_web_search: bool = True) -> LinkedInPost:
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
            "Also provide a detailed image prompt for generating a relevant visual. "
            "Keep the post content between 150-300 words and make it engaging for a professional audience."
        )
        base_user_prompt = f"Create a LinkedIn post about this AI/tech topic: {topic}"
    else:  # personal_milestone
        base_system_prompt = (
            "You are a LinkedIn content creator helping people share personal and professional milestones. "
            "Create an inspiring and authentic LinkedIn post about the given personal achievement or milestone. "
            "The post should be motivational, relatable, and include relevant hashtags. "
            "Also provide a detailed image prompt for generating a relevant visual. "
            "Keep the post content between 100-250 words and make it personal yet professional."
        )
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
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=LinkedInPost,
            ),
        )

        raw_json = response.text
        logging.info(f"Raw JSON from Gemini: {raw_json}")

        if raw_json:
            data = json.loads(raw_json)
            post = LinkedInPost(**data)

            # Add metadata about web search usage
            if search_results:
                logging.info(f"Post generated with web search enhancement. Used {len(search_results)} search results.")

            return post
        else:
            raise ValueError("Empty response from Gemini model")

    except Exception as e:
        raise Exception(f"Failed to generate LinkedIn post: {e}")


def generate_linkedin_post_with_search(topic: str, post_type: str, user_preferences: dict = {}) -> tuple[LinkedInPost, List[Dict[str, Any]]]:
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
    post = generate_linkedin_post(topic, post_type, user_preferences, use_web_search=True)

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
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=LinkedInPost,
            ),
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
        response = client.models.generate_content(
            # IMPORTANT: only this gemini model supports image generation
            model="gemini-2.0-flash-preview-image-generation",
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
        return False
