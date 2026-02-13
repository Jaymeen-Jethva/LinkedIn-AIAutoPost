# Backend Features Required (Future Implementation)

## Navigation Endpoints

### 1. Post History
- **Endpoint**: `/history`
- **Method**: GET
- **Purpose**: Display all previously generated posts
- **Requirements**:
  - Return list of posts with metadata (date, topic, engagement stats if available)
  - Pagination support
  - Filter/search functionality

### 2. Scheduled Posts
- **Endpoint**: `/scheduled`
- **Method**: GET
- **Purpose**: Show posts scheduled for future publishing
- **Requirements**:
  - Return scheduled posts with publish date/time
  - Allow editing scheduled time
  - Cancel/delete scheduled posts

### 3. Settings
- **Endpoint**: `/settings`
- **Method**: GET/POST
- **Purpose**: User preferences and configuration
- **Requirements**:
  - Default tone preference
  - LinkedIn connection settings
  - Notification preferences
  - API key management

## Enhanced Features

### 4. Draft Saving
- Auto-save drafts as user types
- Restore last draft on page load
- Multiple draft management

### 5. Analytics Integration
- Track post performance (views, likes, comments, shares)
- Display engagement metrics in history view
- Export analytics data

### 6. Template Library
- Save custom post templates
- Predefined templates for common scenarios
- Template categorization

## Notes
- All features should follow the glassmorphism design system
- Maintain consistent API response structure
- Implement proper error handling and validation
- Consider adding real-time updates (WebSocket) for scheduled posts

## TODO: Frontend Hardcoded Values

### Post Type / Tone Options
- **Status**: Currently hardcoded in frontend (`App.tsx`)
- **Issue**: Frontend has 5 tone options (professional, viral, story, insightful, direct) but backend only supports 2 post_types (ai_news, personal_milestone)
- **Current Fix**: All tone options are hardcoded to send `post_type: 'ai_news'` to the backend
- **Future Work**: 
  1. Add support for custom tone types in the backend
  2. Update `ALLOWED_POST_TYPES` in `main.py` to include all tones
  3. Modify AI prompt generation to use tone-specific templates
  4. Remove hardcoded value from `frontend/src/App.tsx` and use dynamic tone selection

## TODO: add option for advanced personalization
- prepare a form that will ask some questions to the user about his preferences based on that it will create one persona for AI agents. that will work as a set of rules for AI agents. and will be used to generate posts according to the user's preferences.

## TODO: add option for image generation and web image post save it from web
- prepare a form that will ask some questions to the user about his preferences based on that it will create one image for AI agents. that will work as a set of rules for AI agents. and will be used to generate images according to the user's preferences.
- add option to save image from web and use it in the post. AI agent will fetch the most relevant image from the web and use it in the post.
- add option to upload image and use it in the post. 

## TODO: add option for video/file/image upload
- add option to upload video/file/image and use it in the post.