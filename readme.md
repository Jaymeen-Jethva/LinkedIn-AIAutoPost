# LinkedIn Post Automation System

## Overview
An AI-powered LinkedIn automation system built with LangGraph that generates personalized posts with images based on user topics and preferences. The system includes a complete workflow for content generation, image creation, user approval, and automated posting to LinkedIn.

## Recent Changes (September 28, 2025)
- Created complete LinkedIn automation system using LangGraph workflow orchestration
- Integrated Gemini AI for content generation and image creation (nano banana)
- Built FastAPI web interface with Bootstrap UI for user interaction
- Implemented LinkedIn API integration for automated posting
- Added user approval workflow with revision capabilities
- Set up complete project structure with proper error handling

## User Preferences
- Use Gemini AI only for content creation (not OpenAI)
- System should handle both AI news and personal milestone posts
- Include image generation with posts
- User approval required before posting
- Support for revision based on user feedback

## Project Architecture

### Core Components
1. **Gemini Integration** (`gemini_client.py`)
   - Content generation using Gemini 2.5 Pro
   - Image generation using Gemini 2.0 Flash (nano banana)
   - Post revision capabilities based on feedback

2. **LangGraph Workflow** (`linkedin_workflow.py`)
   - Multi-step workflow orchestration
   - States: content generation → image generation → user approval → posting
   - Error handling and state management
   - Support for revision loops

3. **FastAPI Web Interface** (`main.py`)
   - RESTful API endpoints for post generation and approval
   - Session management for workflow states
   - Web interface serving

4. **LinkedIn API Integration** (`linkedin_api.py`)
   - Text and image posting capabilities
   - OAuth token management
   - Error handling for API failures

5. **Web Interface** (`templates/index.html`)
   - Modern Bootstrap-based UI
   - Modal dialogs for preview and revision
   - Real-time feedback and loading states

### Dependencies
- LangGraph: Workflow orchestration
- FastAPI: Web framework and API
- Gemini AI: Content and image generation
- LinkedIn API: Automated posting
- Bootstrap: Frontend styling
- Uvicorn: ASGI server

### Environment Variables
- `GEMINI_API_KEY`: Required for content generation
- `LINKEDIN_ACCESS_TOKEN`: Optional for real LinkedIn posting
- `LINKEDIN_PERSON_ID`: Optional for real LinkedIn posting

### Workflow States
1. **Content Generation**: Uses Gemini to create post content based on topic and type
2. **Image Generation**: Creates relevant images using Gemini's image capabilities
3. **User Approval**: Presents content for review with revision options
4. **Posting**: Publishes to LinkedIn (simulation mode if API not configured)

## Features
- ✅ Topic-based content generation
- ✅ AI news and personal milestone post types
- ✅ Image generation with nano banana (Gemini)
- ✅ User approval workflow
- ✅ Revision capabilities based on feedback
- ✅ LinkedIn API integration (with simulation fallback)
- ✅ Modern web interface
- ✅ Error handling and validation
- ✅ Session management
- ✅ Real-time updates

## Running the Application
The system runs on port 5000 with the workflow "LinkedIn Automation Server" configured to start automatically.