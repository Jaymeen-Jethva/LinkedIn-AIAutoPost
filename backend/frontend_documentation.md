# LinkedIn AI AutoPost - Frontend Documentation

> **Purpose**: This document provides comprehensive documentation of the frontend architecture, API integrations, UI structure, and implementation details. It's designed to enable AI agents to understand the complete frontend structure and assist with development.

**Last Updated**: 2026-02-07  
**Frontend Version**: 0.0.1  
**Tech Stack**: React 18.3.1 + TypeScript 5.6.2 + Vite 6.0.5

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Tech Stack](#architecture--tech-stack)
3. [Directory Structure](#directory-structure)
4. [API Integration](#api-integration)
5. [TypeScript Types & Interfaces](#typescript-types--interfaces)
6. [Components Documentation](#components-documentation)
7. [State Management & Data Flow](#state-management--data-flow)
8. [Styling System](#styling-system)
9. [Development Configuration](#development-configuration)
10. [Placeholder & TODO Items](#placeholder--todo-items)

---

## Project Overview

The LinkedIn AI AutoPost frontend is a modern, single-page React application that provides an interface for generating AI-powered LinkedIn posts with optional image generation. The application features:

- **AI-Powered Post Generation**: Single-shot or multi-agent post creation
- **LinkedIn OAuth Integration**: Connect and manage LinkedIn accounts
- **Real-time Preview**: Live preview of generated content
- **Image Generation**: Optional AI-generated images for posts
- **Post Revision System**: Request revisions with feedback
- **Glassmorphism Design**: Modern, premium UI with animated gradients

---

## Architecture & Tech Stack

### Core Technologies

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "typescript": "~5.6.2",
  "vite": "^6.0.5"
}
```

### Development Architecture

- **Build Tool**: Vite (port 3000)
- **Language**: TypeScript with strict typing
- **UI Framework**: React with functional components and hooks
- **Styling**: Vanilla CSS with CSS Custom Properties (no Tailwind)
- **State Management**: React useState/useCallback hooks (no external state management)
- **API Layer**: Custom service layer with fetch API
- **Routing**: Single-page application (no routing library)

### Project Structure Philosophy

- **Component-based**: Modular, reusable components
- **Type-safe**: Strong TypeScript typing throughout
- **Service-oriented**: Separate API logic from UI
- **CSS Variables**: Centralized design system with CSS custom properties

---

## Directory Structure

```
frontend/
├── .agent/                     # Agent skills directory
│   └── skills/                 # (docker-expert, vite)
├── index.html                  # Entry HTML file
├── package.json                # Dependencies and scripts
├── vite.config.ts              # Vite configuration with backend proxies
├── tsconfig.json               # TypeScript configuration
└── src/
    ├── main.tsx                # React application entry point
    ├── App.tsx                 # Main application component
    ├── index.css               # Global styles and design system
    ├── vite-env.d.ts           # Vite type declarations
    │
    ├── components/             # React components
    │   ├── common/             # Shared components (5 files)
    │   │   ├── GlassCard.tsx
    │   │   ├── Snackbar.tsx
    │   │   ├── Snackbar.css
    │   │   ├── Spinner.tsx
    │   │   └── index.ts
    │   │
    │   ├── editor/             # Form/input components (10 files)
    │   │   ├── ImageToggle.tsx
    │   │   ├── ImageToggle.css
    │   │   ├── LinkedInStatus.tsx
    │   │   ├── MultiAgentToggle.tsx
    │   │   ├── MultiAgentToggle.css
    │   │   ├── PreferencesInput.tsx
    │   │   ├── StyleSelector.tsx
    │   │   ├── TonePillSelector.tsx
    │   │   ├── TopicInput.tsx
    │   │   └── index.ts
    │   │
    │   ├── layout/             # Layout components (3 files)
    │   │   ├── Sidebar.tsx
    │   │   ├── Sidebar.css
    │   │   └── index.ts
    │   │
    │   └── preview/            # Preview components (4 files)
    │       ├── LinkedInCard.tsx
    │       ├── PreviewColumn.tsx
    │       ├── PreviewModal.tsx
    │       └── index.ts
    │
    ├── config/                 # Configuration
    │   └── api.ts              # API endpoints and base configuration
    │
    ├── hooks/                  # Custom React hooks
    │   └── useSnackbar.ts      # Toast notification system
    │
    ├── services/               # API service layer
    │   ├── linkedInService.ts  # LinkedIn OAuth and connection APIs
    │   └── postService.ts      # Post generation and approval APIs
    │
    ├── types/                  # TypeScript types
    │   └── index.ts            # All type definitions and constants
    │
    └── utils/                  # Utility functions
        └── validation.ts       # Input validation utilities
```

---

## API Integration

### Backend Configuration

**Backend URL**: `http://localhost:8000` (proxied via Vite in development)  
**Protocol**: REST API with JSON payloads  
**Authentication**: User ID stored in `localStorage` (key: `user_id`)

### Vite Proxy Configuration

```typescript
// vite.config.ts
proxy: {
  '/generate-post': { target: 'http://localhost:8000', changeOrigin: true },
  '/approve-post': { target: 'http://localhost:8000', changeOrigin: true },
  '/linkedin': { target: 'http://localhost:8000', changeOrigin: true },
  '/images': { target: 'http://localhost:8000', changeOrigin: true },
  '/static': { target: 'http://localhost:8000', changeOrigin: true }
}
```

### API Endpoints

#### 1. Generate Post - `POST /generate-post`

**Purpose**: Generate a new LinkedIn post using AI

**Request Location**: `src/services/postService.ts:generatePost()`

**Request Parameters**:
- **Query Parameter**: `user_id` (string, required) - Retrieved from `localStorage.getItem('user_id')`

**Request Body**:
```typescript
{
  topic: string;              // User's topic (10-500 chars, validated)
  post_type: string;          // Currently hardcoded to "ai_news"
  user_preferences: {
    general: string;          // User's custom preferences text
    style: PostStyle;         // "storytelling" | "viral" | "tutorial" | "news"
    tone: ToneType;           // "professional" | "viral" | "story" | "insightful" | "direct"
  };
  include_image: boolean;     // Whether to generate an image
  use_multi_agent: boolean;   // Use multi-agent vs single-shot generation
}
```

**Full Request Example**:
```json
POST /generate-post?user_id=abc123xyz

Content-Type: application/json

{
  "topic": "Latest developments in AI and machine learning for enterprise applications",
  "post_type": "ai_news",
  "user_preferences": {
    "general": "Focus on practical applications and ROI",
    "style": "news",
    "tone": "professional"
  },
  "include_image": true,
  "use_multi_agent": false
}
```

**Response**:
```typescript
{
  session_id: string;         // Unique session identifier
  content: string;            // Generated post content
  hashtags: string[];         // Array of hashtags (e.g., ["#AI", "#MachineLearning"])
  image_path?: string;        // Optional: Path to generated image (e.g., "images/abc123.png")
  image_prompt?: string;      // Optional: Prompt used for image generation
}
```

**Response Example**:
```json
{
  "session_id": "sess_789xyz456",
  "content": "Exciting developments in AI and machine learning! 🚀\n\nThe latest insights are reshaping how we approach enterprise applications...",
  "hashtags": ["#AI", "#MachineLearning", "#Enterprise", "#Innovation"],
  "image_path": "generated/sess_789xyz456_image.png",
  "image_prompt": "Modern office with AI technology, futuristic design, professional lighting"
}
```

**Error Handling**:
```typescript
// Error Response (non-OK status)
{
  detail: string;  // Error message
}

// Frontend catches and displays error.detail or generic message
```

**Called From**: 
- `src/App.tsx:handleSubmit()` (line 67)
- Triggered by form submission in editor column

---

#### 2. Approve Post - `POST /approve-post`

**Purpose**: Approve and publish a post, or request revision with feedback

**Request Location**: `src/services/postService.ts:approvePost()`

**Request Parameters**: None

**Request Body**:
```typescript
{
  session_id: string;     // Session ID from generate-post response
  approved: boolean;      // true = publish, false = request revision
  feedback?: string;      // Optional: Feedback for revision (required if approved=false)
}
```

**Approval Request Example**:
```json
POST /approve-post

Content-Type: application/json

{
  "session_id": "sess_789xyz456",
  "approved": true
}
```

**Revision Request Example**:
```json
POST /approve-post

Content-Type: application/json

{
  "session_id": "sess_789xyz456",
  "approved": false,
  "feedback": "Make it more casual and add a personal story about implementing AI in my company"
}
```

**Response (Approval)**:
```typescript
{
  success: boolean;       // true if post was published successfully
  message?: string;       // Success/error message
}
```

**Response (Revision)**:
```typescript
{
  revised: boolean;           // true if revision was successful
  content?: string;           // Updated post content
  hashtags?: string[];        // Updated hashtags
  image_path?: string;        // Updated image path
  image_prompt?: string;      // Updated image prompt
}
```

**Response Example (Approval)**:
```json
{
  "success": true,
  "message": "Post published successfully to LinkedIn"
}
```

**Response Example (Revision)**:
```json
{
  "revised": true,
  "content": "Let me share a story about implementing AI in my company...",
  "hashtags": ["#AIStory", "#Leadership", "#Innovation"],
  "image_path": "generated/sess_789xyz456_revised.png"
}
```

**Called From**: 
- `src/App.tsx:handleApprove()` (line 95) - For approvals
- `src/App.tsx:handleRevise()` (line 119) - For revisions
- Triggered by buttons in PreviewModal component

---

#### 3. LinkedIn Status - `GET /linkedin/status`

**Purpose**: Check if user's LinkedIn account is connected

**Request Location**: `src/services/linkedInService.ts:getLinkedInStatus()`

**Request Parameters**:
- **Query Parameter**: `user_id` (string, optional) - Retrieved from `localStorage.getItem('user_id')`

**Request Example**:
```
GET /linkedin/status?user_id=abc123xyz
```

**Response**:
```typescript
{
  connected: boolean;   // true if LinkedIn is connected, false otherwise
}
```

**Response Example**:
```json
{
  "connected": true
}
```

**Called From**:
- `src/components/editor/LinkedInStatus.tsx:checkStatus()` (line 22)
- Triggered on component mount and after OAuth redirect

---

#### 4. LinkedIn Connect - `POST /linkedin/connect`

**Purpose**: Initiate LinkedIn OAuth flow

**Request Location**: `src/services/linkedInService.ts:connectLinkedIn()`

**Request Parameters**: None

**Request Body**: Empty (POST with no body)

**Request Example**:
```
POST /linkedin/connect

Content-Type: application/json
```

**Response**:
```typescript
{
  authorization_url?: string;   // LinkedIn OAuth URL to redirect to
  detail?: string;              // Error message if failed
}
```

**Response Example (Success)**:
```json
{
  "authorization_url": "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=..."
}
```

**Response Example (Error)**:
```json
{
  "detail": "OAuth configuration not available"
}
```

**OAuth Redirect Flow**:
1. User clicks "Connect" button
2. Frontend calls `/linkedin/connect`
3. Backend returns `authorization_url`
4. Frontend redirects: `window.location.href = authorization_url`
5. User authorizes on LinkedIn
6. LinkedIn redirects back to frontend with query params:
   - Success: `?linkedin_connected=true&user_id=abc123xyz`
   - Error: `?linkedin_error=error_message`
7. Frontend parses params and stores `user_id` in localStorage

**Called From**:
- `src/components/editor/LinkedInStatus.tsx:handleConnect()` (line 61)
- Triggered by "Connect" button click

---

#### 5. LinkedIn Disconnect - `POST /linkedin/disconnect`

**Purpose**: Disconnect LinkedIn account and revoke tokens

**Request Location**: `src/services/linkedInService.ts:disconnectLinkedIn()`

**Request Parameters**:
- **Query Parameter**: `user_id` (string, required) - Retrieved from `localStorage.getItem('user_id')`

**Request Example**:
```
POST /linkedin/disconnect?user_id=abc123xyz

Content-Type: application/json
```

**Response**:
```typescript
{
  success: boolean;   // true if disconnected successfully
  detail?: string;    // Error message if failed
}
```

**Response Example (Success)**:
```json
{
  "success": true
}
```

**Response Example (Error)**:
```json
{
  "success": false,
  "detail": "User not found"
}
```

**Called From**:
- `src/components/editor/LinkedInStatus.tsx:handleDisconnect()` (line 84)
- Triggered by "Disconnect" button click with confirmation dialog

---

### API Helper Function

**Location**: `src/config/api.ts`

```typescript
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T>
```

**Features**:
- Automatically adds `Content-Type: application/json` header
- Handles non-OK responses by parsing error detail
- Throws errors with backend error messages
- Returns typed response based on generic parameter

**Usage Example**:
```typescript
const result = await apiRequest<GeneratedPost>('/generate-post?user_id=123', {
  method: 'POST',
  body: JSON.stringify({ topic: 'AI news', ... })
});
```

---

## TypeScript Types & Interfaces

**Location**: `src/types/index.ts`

### API Request Types

```typescript
// Post generation request
interface PostRequest {
  topic: string;
  post_type: string;
  user_preferences: Record<string, string>;
  include_image: boolean;
  use_multi_agent: boolean;
}

// Post approval/revision request
interface ApprovalRequest {
  session_id: string;
  approved: boolean;
  feedback?: string;
}
```

### API Response Types

```typescript
// Generated post response
interface GeneratedPost {
  session_id: string;
  content: string;
  hashtags: string[];
  image_path?: string;
  image_prompt?: string;
}

// Approval response
interface ApprovalResponse {
  success?: boolean;      // For approvals
  message?: string;
  revised?: boolean;      // For revisions
  content?: string;
  hashtags?: string[];
  image_path?: string;
  image_prompt?: string;
}

// LinkedIn status
interface LinkedInStatus {
  connected: boolean;
}

// LinkedIn connect response
interface LinkedInConnectResponse {
  authorization_url?: string;
  detail?: string;
}

// LinkedIn disconnect response
interface LinkedInDisconnectResponse {
  success: boolean;
  detail?: string;
}
```

### UI State Types

```typescript
// Tone types
type ToneType = 'professional' | 'viral' | 'story' | 'insightful' | 'direct';

interface ToneOption {
  value: ToneType;
  label: string;
  emoji: string;
}

const TONE_OPTIONS: ToneOption[] = [
  { value: 'professional', label: 'Professional', emoji: '👔' },
  { value: 'viral', label: 'Viral', emoji: '🚀' },
  { value: 'story', label: 'Story', emoji: '📖' },
  { value: 'insightful', label: 'Insightful', emoji: '💡' },
  { value: 'direct', label: 'Direct', emoji: '🎯' }
];

// Post style types
type PostStyle = 'storytelling' | 'viral' | 'tutorial' | 'news';

interface StyleOption {
  value: PostStyle;
  label: string;
  emoji: string;
  description: string;
}

const STYLE_OPTIONS: StyleOption[] = [
  {
    value: 'storytelling',
    label: 'Storytelling',
    emoji: '📖',
    description: 'Personal experience, humanized, authentic'
  },
  {
    value: 'viral',
    label: 'Viral / Trends',
    emoji: '🚀',
    description: 'Short hooks, pop culture, high engagement'
  },
  {
    value: 'tutorial',
    label: 'Tutorial / Deep Dive',
    emoji: '📚',
    description: 'Educational, technical, analyzing concepts'
  },
  {
    value: 'news',
    label: 'Industry News',
    emoji: '📰',
    description: 'Updates, analysis of current events'
  }
];
```

### Validation Constants

```typescript
const MIN_TOPIC_LENGTH = 10;
const MAX_TOPIC_LENGTH = 500;
const DANGEROUS_CHARS_PATTERN = /[<>{}|\\^`]/;
```

---

## Components Documentation

### App.tsx (Main Application)

**Location**: `src/App.tsx`  
**Purpose**: Root component managing application state and orchestrating all functionality

**State Variables**:
```typescript
// Form state
const [topic, setTopic] = useState<string>('');
const [tone, setTone] = useState<ToneType>('professional');
const [style, setStyle] = useState<PostStyle>('news');
const [includeImage, setIncludeImage] = useState<boolean>(true);
const [useMultiAgent, setUseMultiAgent] = useState<boolean>(false);
const [preferences, setPreferences] = useState<string>('');

// UI state
const [isLoading, setIsLoading] = useState<boolean>(false);
const [error, setError] = useState<string | null>(null);
const [currentPost, setCurrentPost] = useState<GeneratedPost | null>(null);
const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
const [isModalLoading, setIsModalLoading] = useState<boolean>(false);
```

**Key Functions**:

1. **handleSubmit** (line 45):
   - Validates topic input
   - Retrieves user_id from localStorage
   - Calls generatePost API
   - Opens preview modal with generated post

2. **handleApprove** (line 90):
   - Calls approvePost API with approved=true
   - Shows success snackbar
   - Resets form and closes modal

3. **handleRevise** (line 114):
   - Calls approvePost API with approved=false and feedback
   - Updates currentPost with revised content
   - Shows revision success snackbar

**Layout Structure**:
```jsx
<>
  {/* Animated gradient orbs background */}
  <div className="orb-container">...</div>
  
  <div className="app-container">
    <Sidebar />
    
    <main className="main-content">
      {/* Left: Editor Column */}
      <section className="editor-column">
        <LinkedInStatus />
        <form onSubmit={handleSubmit}>
          <TopicInput />
          <StyleSelector />
          <TonePillSelector />
          <ImageToggle />
          <MultiAgentToggle />
          <PreferencesInput />
          <button type="submit">Generate Post</button>
        </form>
      </section>
      
      {/* Right: Preview Column */}
      <PreviewColumn />
    </main>
  </div>
  
  {/* Modal */}
  <PreviewModal />
  
  {/* Notifications */}
  <Snackbar />
</>
```

---

### Common Components

#### GlassCard.tsx

**Location**: `src/components/common/GlassCard.tsx`  
**Purpose**: Reusable glass-effect card component

**Props**:
```typescript
interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}
```

**Usage**:
```jsx
<GlassCard className="mb-3" style={{ padding: '1rem' }}>
  {/* Content */}
</GlassCard>
```

---

#### Spinner.tsx

**Location**: `src/components/common/Spinner.tsx`  
**Purpose**: Loading spinner with message

**Props**:
```typescript
interface SpinnerProps {
  message?: string;
  subMessage?: string;
}
```

**Usage**:
```jsx
<Spinner 
  message="Generating your post..." 
  subMessage="This usually takes 10-30 seconds"
/>
```

---

#### Snackbar.tsx

**Location**: `src/components/common/Snackbar.tsx`  
**Purpose**: Toast notification system

**Props**:
```typescript
interface SnackbarProps {
  messages: SnackbarMessage[];
  onDismiss: (id: string) => void;
}

interface SnackbarMessage {
  id: string;
  message: string;
}
```

**Hook Integration**:
```typescript
// In App.tsx
const { messages, showSnackbar, dismissSnackbar } = useSnackbar();

// Show notification
showSnackbar('Post published successfully!', 5000);

// Render
<Snackbar messages={messages} onDismiss={dismissSnackbar} />
```

---

### Editor Components

#### TopicInput.tsx

**Location**: `src/components/editor/TopicInput.tsx`  
**Purpose**: Multi-line text input for post topic with character counter

**Props**:
```typescript
interface TopicInputProps {
  value: string;
  onChange: (value: string) => void;
}
```

**Features**:
- Character counter with color coding (normal/warning/danger)
- Placeholder text with examples
- Auto-resize textarea (5 rows default)

---

#### StyleSelector.tsx

**Location**: `src/components/editor/StyleSelector.tsx`  
**Purpose**: Grid-based style selector with descriptions

**Props**:
```typescript
interface StyleSelectorProps {
  value: PostStyle;
  onChange: (style: PostStyle) => void;
}
```

**UI Layout**:
- 2-column grid
- Each option shows emoji, label, and description
- Active state with gradient background

---

#### TonePillSelector.tsx

**Location**: `src/components/editor/TonePillSelector.tsx`  
**Purpose**: Horizontal pill-based tone selector

**Props**:
```typescript
interface TonePillSelectorProps {
  value: ToneType;
  onChange: (tone: ToneType) => void;
}
```

**Features**:
- Scrollable horizontal layout
- Pills with emoji + label
- Active state with gradient background and glow effect

---

#### ImageToggle.tsx

**Location**: `src/components/editor/ImageToggle.tsx`  
**Purpose**: Toggle switch for image generation

**Props**:
```typescript
interface ImageToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
}
```

**Features**:
- Custom toggle switch with smooth animation
- Subtitle explaining feature
- CSS-based toggle (no external library)

---

#### MultiAgentToggle.tsx

**Location**: `src/components/editor/MultiAgentToggle.tsx`  
**Purpose**: Toggle for multi-agent vs single-shot generation

**Props**:
```typescript
interface MultiAgentToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
}
```

**Features**:
- Badge-style toggle with detailed descriptions for each mode
- Visual indicators for quality/speed tradeoff

---

#### PreferencesInput.tsx

**Location**: `src/components/editor/PreferencesInput.tsx`  
**Purpose**: Optional textarea for custom user preferences

**Props**:
```typescript
interface PreferencesInputProps {
  value: string;
  onChange: (value: string) => void;
}
```

**Features**:
- Optional field (not required)
- Placeholder with examples
- Textarea with 3 rows default

---

#### LinkedInStatus.tsx

**Location**: `src/components/editor/LinkedInStatus.tsx`  
**Purpose**: LinkedIn connection status indicator and OAuth controls

**Props**:
```typescript
interface LinkedInStatusProps {
  showSnackbar: (message: string, duration?: number) => void;
}
```

**State**:
```typescript
const [isConnected, setIsConnected] = useState<boolean>(false);
const [isLoading, setIsLoading] = useState<boolean>(false);
```

**Key Functions**:

1. **checkStatus** (line 22):
   - Retrieves user_id from localStorage
   - Calls getLinkedInStatus API
   - Updates connection status

2. **handleOAuthRedirect** (line 38):
   - Parses URL query parameters on mount
   - Handles `?linkedin_connected=true&user_id=xyz` success
   - Handles `?linkedin_error=message` failure
   - Stores user_id in localStorage
   - Cleans up URL parameters

3. **handleConnect** (line 58):
   - Calls connectLinkedIn API
   - Redirects to authorization_url

4. **handleDisconnect** (line 73):
   - Shows confirmation dialog
   - Calls disconnectLinkedIn API
   - Removes user_id from localStorage
   - Updates connection status

**UI States**:
- **Connected**: Green dot indicator + "Disconnect" button
- **Not Connected**: Gray dot indicator + "Connect" button

---

### Preview Components

#### PreviewColumn.tsx

**Location**: `src/components/preview/PreviewColumn.tsx`  
**Purpose**: Right column showing live preview of post

**Props**:
```typescript
interface PreviewColumnProps {
  topic: string;
  tone: ToneType;
  preferences: string;
  includeImage: boolean;
}
```

**Features**:
- Generates mock content based on topic + tone
- Auto-generates hashtags from topic keywords
- Shows "Preview Mode" badge
- Displays LinkedInCard component with mock data

**Preview Content Generation** (line 18):
```typescript
const { content, hashtags } = useMemo(() => {
  // If topic too short, show placeholder
  if (topic.length < 10) return { content: 'Fill out the form...', hashtags: [] };
  
  // Select template based on tone
  // Add preferences note if provided
  // Generate hashtags from topic words
  
  return { content, hashtags };
}, [topic, tone, preferences]);
```

---

#### LinkedInCard.tsx

**Location**: `src/components/preview/LinkedInCard.tsx`  
**Purpose**: Mock LinkedIn post card UI

**Props**:
```typescript
interface LinkedInCardProps {
  content: string;
  hashtags: string[];
  showImage: boolean;
}
```

**UI Structure**:
```jsx
<div className="linkedin-card">
  {/* Header: Avatar + Name + Meta */}
  <div className="linkedin-card-header">
    <div className="linkedin-profile">
      <div className="linkedin-avatar">YU</div>
      <div className="linkedin-user-info">
        <div className="linkedin-name">Your Name</div>
        <div className="linkedin-meta">Just now • 🌎</div>
      </div>
    </div>
  </div>
  
  {/* Content */}
  <div className="linkedin-content">
    <p className="linkedin-text">{content}</p>
    {showImage && <div className="linkedin-image-placeholder">🖼️ AI-Generated Image</div>}
    <div className="linkedin-hashtags">{hashtags}</div>
  </div>
  
  {/* Footer: Like/Comment/Share buttons */}
  <div className="linkedin-footer">...</div>
</div>
```

---

#### PreviewModal.tsx

**Location**: `src/components/preview/PreviewModal.tsx`  
**Purpose**: Modal for reviewing and approving/revising generated posts

**Props**:
```typescript
interface PreviewModalProps {
  isOpen: boolean;
  post: GeneratedPost | null;
  onClose: () => void;
  onApprove: () => Promise<void>;
  onRevise: (feedback: string) => Promise<void>;
  isLoading: boolean;
}
```

**State**:
```typescript
const [showRevisionInput, setShowRevisionInput] = useState<boolean>(false);
const [feedback, setFeedback] = useState<string>('');
```

**UI States**:

1. **Initial State** (showRevisionInput=false):
   - Shows generated content, hashtags, image
   - Buttons: "Cancel", "Request Revision", "Approve & Post"

2. **Revision State** (showRevisionInput=true):
   - Shows all content + feedback textarea
   - Buttons: "Cancel", "Submit Revision Request"

3. **Loading State** (isLoading=true):
   - Disables all buttons
   - Shows "Posting..." or "Revising..." text

**Image Display Logic** (line 125):
```typescript
if (post.image_path) {
  // Show actual generated image
  <img src={`/images/${post.image_path.split('/').pop()}`} />
} else if (post.image_prompt) {
  // Show prompt + warning (image generation failed but will retry on approve)
  <p>Image Prompt: {post.image_prompt}</p>
  <p>⚠️ Image generation failed, but will be retried if you approve.</p>
}
```

---

### Layout Components

#### Sidebar.tsx

**Location**: `src/components/layout/Sidebar.tsx`  
**Purpose**: Collapsible navigation sidebar

**State**:
```typescript
const [isExpanded, setIsExpanded] = useState<boolean>(() => {
  return localStorage.getItem('sidebarExpanded') === 'true';
});
const [activePage, setActivePage] = useState<string>('create');
```

**Navigation Items**:
```typescript
const NAV_ITEMS: NavItem[] = [
  { id: 'create', label: 'Create', icon: '✨' },
  { id: 'history', label: 'History', icon: '📜' },      // Placeholder
  { id: 'scheduled', label: 'Scheduled', icon: '📅' },  // Placeholder
  { id: 'settings', label: 'Settings', icon: '⚙️' }     // Placeholder
];
```

**Features**:
- Persists expanded state in localStorage
- Smooth expand/collapse animation
- Only "Create" page is functional (others log to console)
- Toggle button in footer

**CSS Classes**:
- `.sidebar` - Base collapsed (64px width)
- `.sidebar.expanded` - Expanded (240px width)
- Transitions controlled by CSS custom properties

---

### Hooks

#### useSnackbar

**Location**: `src/hooks/useSnackbar.ts`  
**Purpose**: Manage toast notification queue

**API**:
```typescript
const { messages, showSnackbar, dismissSnackbar } = useSnackbar();

// Show notification (auto-dismisses after duration)
showSnackbar(message: string, duration: number = 4000);

// Manually dismiss
dismissSnackbar(id: string);
```

**Implementation**:
- Uses `crypto.randomUUID()` for unique IDs
- Auto-dismisses with setTimeout
- Handles multiple concurrent messages

---

### Utilities

#### validation.ts

**Location**: `src/utils/validation.ts`  
**Purpose**: Input validation for topic field

**Function**:
```typescript
function validateTopic(topic: string): ValidationResult {
  // Returns { isValid: boolean, error?: string }
}
```

**Validation Rules**:
1. Topic cannot be empty
2. Must be at least 10 characters
3. Cannot exceed 500 characters
4. Cannot contain dangerous characters: `< > { } | \ ^ \``

**Usage**:
```typescript
const validation = validateTopic(topic);
if (!validation.isValid) {
  setError(validation.error!);
  return;
}
```

---

## State Management & Data Flow

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        App.tsx (Root)                       │
│  - Form State: topic, tone, style, includeImage, etc.      │
│  - UI State: isLoading, error, currentPost, isModalOpen    │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼──────────┐  ┌──────▼──────────┐
│  Editor Column   │  │ Preview Column  │
│  - Input forms   │  │ - Live preview  │
│  - User actions  │  │ - Mock data     │
└───────┬──────────┘  └─────────────────┘
        │
        │ Form Submit
        ▼
┌────────────────────────────────────┐
│  postService.generatePost()         │
│  → POST /generate-post?user_id=xxx │
└────────────────┬───────────────────┘
                 │
                 │ Response
                 ▼
┌────────────────────────────────────┐
│  App.setCurrentPost()               │
│  App.setIsModalOpen(true)          │
└────────────────┬───────────────────┘
                 │
                 │ Opens modal
                 ▼
┌────────────────────────────────────┐
│  PreviewModal                       │
│  - Displays post                   │
│  - Approve or Revise buttons       │
└────────────────┬───────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
 Approve│                 │Revise
        │                 │
        ▼                 ▼
┌─────────────┐    ┌──────────────┐
│ Approve API │    │  Revise API  │
│ → Publish   │    │ → Update     │
│   to LI     │    │   currentPost│
└─────────────┘    └──────────────┘
```

### State Flow Patterns

#### 1. Post Generation Flow

```typescript
// User fills form → submits
handleSubmit() {
  // 1. Validate
  validateTopic(topic)
  
  // 2. Check user_id
  userId = localStorage.getItem('user_id')
  
  // 3. Call API
  setIsLoading(true)
  result = await generatePost({...})
  
  // 4. Update state
  setCurrentPost(result)
  setIsModalOpen(true)
  setIsLoading(false)
}
```

#### 2. Approval Flow

```typescript
handleApprove() {
  setIsModalLoading(true)
  result = await approvePost(sessionId, true)
  
  if (result.success) {
    setIsModalOpen(false)
    showSnackbar('Post published!')
    // Reset form
    setTopic('')
    setPreferences('')
    setCurrentPost(null)
  }
  setIsModalLoading(false)
}
```

#### 3. Revision Flow

```typescript
handleRevise(feedback) {
  setIsModalLoading(true)
  result = await approvePost(sessionId, false, feedback)
  
  if (result.revised) {
    // Update current post with revised content
    setCurrentPost({
      ...currentPost,
      content: result.content,
      hashtags: result.hashtags,
      image_path: result.image_path
    })
    showSnackbar('Content revised!')
  }
  setIsModalLoading(false)
}
```

#### 4. LinkedIn OAuth Flow

```typescript
// Step 1: Connect
handleConnect() {
  response = await connectLinkedIn()
  window.location.href = response.authorization_url
}

// Step 2: Handle redirect (on mount)
handleOAuthRedirect() {
  params = new URLSearchParams(window.location.search)
  
  if (params.has('linkedin_connected')) {
    userId = params.get('user_id')
    localStorage.setItem('user_id', userId)
    showSnackbar('Connected!')
    // Clean URL
    window.history.replaceState({}, '', '/')
    checkStatus()
  }
}
```

### LocalStorage Usage

**Key**: `user_id`  
**Purpose**: Store authenticated user ID from LinkedIn OAuth  
**Lifecycle**:
- Set by: `LinkedInStatus.handleOAuthRedirect()` after successful OAuth
- Read by: All API calls requiring authentication
- Removed by: `LinkedInStatus.handleDisconnect()`

**Key**: `sidebarExpanded`  
**Purpose**: Persist sidebar expanded/collapsed state  
**Values**: `"true"` or `"false"` (string)  
**Lifecycle**:
- Set by: `Sidebar` component on toggle
- Read by: `Sidebar` component on mount

---

## Styling System

### Design Philosophy

**Glassmorphism 2.0**: Modern, premium UI with frosted glass effects, animated gradients, and smooth micro-animations.

### Color System

```css
/* Background Colors - Deep Obsidian Theme */
--bg-primary: #0f172a;      /* Main dark background */
--bg-secondary: #1e293b;    /* Card backgrounds */
--bg-tertiary: #334155;     /* Elevated elements */

/* Text Colors */
--text-primary: #f8fafc;    /* Headings, important text */
--text-secondary: #cbd5e1;  /* Body text */
--text-muted: #94a3b8;      /* Labels, meta text */
--text-dim: #64748b;        /* Placeholder, disabled */

/* Brand Colors - Gradient Palette */
--primary: #6366f1;         /* Indigo */
--primary-light: #818cf8;
--primary-dark: #4f46e5;
--secondary: #8b5cf6;       /* Purple */
--accent-cyan: #06b6d4;
--accent-purple: #9333ea;

/* Status Colors */
--success: #10b981;
--warning: #f59e0b;
--danger: #ef4444;
--info: #3b82f6;
```

### Glass Effects

```css
/* Glass Background */
--glass-bg: rgba(255, 255, 255, 0.03);
--glass-bg-hover: rgba(255, 255, 255, 0.06);

/* Glass Borders - 3D effect */
--glass-border: rgba(255, 255, 255, 0.1);
--glass-border-top: rgba(255, 255, 255, 0.15);    /* Lighter top */
--glass-border-bottom: rgba(0, 0, 0, 0.4);        /* Darker bottom */
--glass-border-side: rgba(255, 255, 255, 0.05);

/* Applied with backdrop-filter */
backdrop-filter: blur(16px) saturate(180%);
```

### Shadows & Glows

```css
/* Shadows */
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
--shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
--shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);
--shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.5);

/* Glows - for active/focus states */
--glow-primary: 0 0 20px rgba(99, 102, 241, 0.3);
--glow-purple: 0 0 30px rgba(139, 92, 246, 0.4);
--glow-cyan: 0 0 25px rgba(6, 182, 212, 0.3);
```

### Typography

```css
/* Fonts */
font-family: 'Inter', sans-serif;           /* Body text */
font-family: 'JetBrains Mono', monospace;   /* Labels, badges, code */

/* Google Fonts Import */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
```

### Animations

#### 1. Gradient Orbs Animation

```css
.orb {
  animation: float 40s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(50px, -50px) rotate(90deg); }
  50% { transform: translate(-30px, 30px) rotate(180deg); }
  75% { transform: translate(40px, 60px) rotate(270deg); }
}
```

**Orb Configuration**:
- Orb 1: Purple gradient, top-left, 40s duration
- Orb 2: Blue gradient, right, 50s duration, -10s delay
- Orb 3: Cyan gradient, bottom, 45s duration, -20s delay

#### 2. Transition System

```css
--transition-speed: 0.3s;
--transition-smooth: cubic-bezier(0.4, 0, 0.2, 1);

/* Applied to interactive elements */
transition: all var(--transition-speed) var(--transition-smooth);
```

### Component-Specific Styles

#### Glass Card Pattern

```css
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid var(--glass-border);
  border-top-color: var(--glass-border-top);
  border-bottom-color: var(--glass-border-bottom);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
}
```

#### Magic Button (Primary CTA)

```css
.magic-button {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  box-shadow: var(--shadow-md), var(--glow-purple);
  
  /* Shimmer effect on hover */
  &::before {
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: shimmer 0.6s;
  }
}
```

#### Tone Pills

```css
.tone-pill {
  background: var(--glass-bg);
  border-radius: 999px;
  transition: all 0.3s;
}

.tone-pill.active {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  box-shadow: var(--glow-primary);
}
```

### Responsive Design

**Breakpoint**: 1024px

```css
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;  /* Stack columns vertically */
  }
  
  .preview-column {
    display: none;  /* Hide preview on mobile */
  }
}
```

### Custom Scrollbar

```css
.editor-column::-webkit-scrollbar {
  width: 8px;
}

.editor-column::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.editor-column::-webkit-scrollbar-thumb {
  background: var(--glass-border);
  border-radius: 4px;
}

.editor-column::-webkit-scrollbar-thumb:hover {
  background: var(--primary);
}
```

---

## Development Configuration

### Package Scripts

```json
{
  "dev": "vite --port 3000",
  "build": "tsc -b && vite build",
  "lint": "eslint .",
  "preview": "vite preview --port 3000"
}
```

### TypeScript Configuration

**File**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "strict": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Vite Configuration

**File**: `vite.config.ts`

**Key Features**:
- React plugin for Fast Refresh
- Path alias: `@` → `./src`
- Dev server on port 3000
- Backend proxy to localhost:8000
- Source maps in production build

### Environment Setup

**Development**:
```bash
npm install
npm run dev
```

**Build**:
```bash
npm run build
# Output: dist/
```

**Dependencies**:
- Node.js (recommended: v18+)
- npm (comes with Node.js)

### Backend Integration

**Required Backend URL**: `http://localhost:8000`

**Proxied Paths**:
- `/generate-post` → Backend API
- `/approve-post` → Backend API
- `/linkedin/*` → Backend OAuth endpoints
- `/images/*` → Generated images storage
- `/static/*` → Static assets

---

## Placeholder & TODO Items

### 1. Sidebar Navigation - Placeholder Pages

**Location**: `src/components/layout/Sidebar.tsx`

**Status**: ⚠️ PLACEHOLDER

**Current State**:
- Navigation items defined: History, Scheduled, Settings
- Only "Create" page is functional
- Other pages log to console: `console.log(\`Navigation to ${pageId} - Backend endpoint required\`)`

**TODO**:
- Implement `/history` page showing past generated posts
- Implement `/scheduled` page for scheduled posts (future feature)
- Implement `/settings` page for user preferences/configuration
- Create backend endpoints for these features
- Implement routing (currently single-page app)

**Code Reference** (line 31):
```typescript
const handleNavClick = (pageId: string) => {
  setActivePage(pageId);
  if (pageId !== 'create') {
    console.log(`Navigation to ${pageId} - Backend endpoint required`);
  }
};
```

---

### 2. Post Type - Hardcoded Value

**Location**: `src/App.tsx` (line 69-70)

**Status**: ⚠️ TODO

**Current State**:
```typescript
// TODO: Currently hardcoded to 'ai_news' - update when backend supports custom tone types
post_type: 'ai_news',
```

**Issue**: `post_type` is always sent as `"ai_news"` regardless of user's tone selection

**Expected Behavior**: `post_type` should derive from or complement the selected `tone` and `style`

**TODO**:
- Confirm backend's expected `post_type` values
- Map frontend `tone` + `style` to backend `post_type`
- Remove hardcoded value
- Update TypeScript types if needed

**Possible Solution**:
```typescript
// Option 1: Map style to post_type
post_type: style, // "storytelling" | "viral" | "tutorial" | "news"

// Option 2: Create mapping function
const getPostType = (style: PostStyle, tone: ToneType) => {
  // Custom logic
  return mapToBackendType(style, tone);
}
```

---

### 3. LinkedIn Profile Mock Data

**Location**: `src/components/preview/LinkedInCard.tsx`

**Status**: ⚠️ PLACEHOLDER

**Current State**:
- Avatar shows hardcoded "YU"
- Name shows "Your Name"
- No actual user data integration

**TODO**:
- Fetch actual LinkedIn profile data after OAuth
- Store profile info (name, photo, headline) in state or context
- Display real user data in preview
- Backend should return profile info after OAuth callback

**Code Reference**:
```tsx
<div className="linkedin-avatar">YU</div>
<div className="linkedin-name">Your Name</div>
```

**Expected Flow**:
1. After LinkedIn OAuth, backend returns user profile
2. Frontend stores profile data
3. Preview shows actual name and avatar

---

### 4. Image Path Handling - Potential Issue

**Location**: `src/components/preview/PreviewModal.tsx` (line 138)

**Status**: ⚠️ VERIFY

**Current Code**:
```tsx
<img src={`/images/${post.image_path.split('/').pop()}`} alt="Generated image" />
```

**Potential Issues**:
- Assumes `image_path` from backend contains `/` separators (may be Windows `\` on backend)
- Uses `.split('/').pop()` to extract filename, might not work if backend sends full path
- Relies on Vite proxy to serve `/images/*` correctly

**TODO**:
- Verify backend's `image_path` format (e.g., "generated/abc123.png" vs "f:/backend/generated/abc123.png")
- Test on Windows backend to ensure path separators work
- Consider normalizing path handling in a utility function

**Recommended Solution**:
```typescript
// In utils/path.ts
export function getImageUrl(imagePath: string): string {
  const filename = imagePath.replace(/\\/g, '/').split('/').pop();
  return `/images/${filename}`;
}
```

---

### 5. Error Handling - No Retry Logic

**Location**: `src/services/*.ts`, `src/App.tsx`

**Status**: ⚠️ TODO

**Current State**:
- API errors are caught and displayed as alerts/errors
- No retry mechanism for failed requests
- No handling of network timeouts

**TODO**:
- Implement retry logic for transient failures (network issues, 5xx errors)
- Add timeout handling
- Distinguish between retryable and non-retryable errors
- Show appropriate error messages to user

**Example Enhancement**:
```typescript
async function apiRequestWithRetry<T>(
  endpoint: string,
  options: RequestInit,
  maxRetries = 3
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiRequest<T>(endpoint, options);
    } catch (error) {
      if (i === maxRetries - 1 || !isRetryable(error)) throw error;
      await delay(1000 * (i + 1)); // Exponential backoff
    }
  }
}
```

---

### 6. Form Validation - Client-Side Only

**Location**: `src/utils/validation.ts`, `src/App.tsx`

**Status**: ⚠️ INCOMPLETE

**Current State**:
- Only `topic` field is validated
- No validation for `preferences` field
- No validation for `style` and `tone` (assumed valid from UI)

**Gaps**:
- Backend may reject overly long `preferences`
- No validation of combined form state
- No regex validation for special use cases

**TODO**:
- Add validation for `preferences` field (max length?)
- Add comprehensive form validation before submission
- Match validation rules with backend expectations
- Show field-specific error messages

---

### 7. LinkedIn OAuth - No Error State UI

**Location**: `src/components/editor/LinkedInStatus.tsx`

**Status**: ⚠️ INCOMPLETE

**Current Behavior**:
- OAuth errors show in snackbar: `❌ LinkedIn connection failed: {error}`
- No persistent error state in UI
- No retry button after failure

**TODO**:
- Add error state display in LinkedInStatus component
- Show "Retry" button after OAuth failure
- Display helpful error messages (e.g., "OAuth not configured" vs "User denied")
- Link to troubleshooting docs

---

### 8. Snackbar Queue - No Limit

**Location**: `src/hooks/useSnackbar.ts`

**Status**: ⚠️ POTENTIAL ISSUE

**Current Behavior**:
- Unlimited snackbar messages can pile up
- No maximum queue size
- All messages display simultaneously (may overflow UI)

**TODO**:
- Implement queue limit (e.g., max 3 concurrent messages)
- Add FIFO queue when limit exceeded
- Consider dismissing old messages when new ones arrive

**Example Enhancement**:
```typescript
const MAX_MESSAGES = 3;

const showSnackbar = (message: string, duration = 4000) => {
  setMessages(prev => {
    const newMessages = [...prev, { id, message }];
    return newMessages.slice(-MAX_MESSAGES); // Keep only last N
  });
};
```

---

### 9. Image Generation Retry - Not Implemented

**Location**: `src/components/preview/PreviewModal.tsx` (line 158-160)

**Warning Message**:
```tsx
<p style={{ color: 'var(--warning)' }}>
  ⚠️ Image generation failed, but will be retried if you approve.
</p>
```

**Status**: ⚠️ VERIFY WITH BACKEND

**Question**: Does the backend actually retry image generation on approval?

**TODO**:
- Verify backend implements retry logic
- If not implemented, either:
  - Implement retry in backend
  - OR remove the promise from UI
  - OR add manual "Regenerate Image" button

---

### 10. Responsive Design - Incomplete

**Location**: `src/index.css` (line 797+)

**Status**: ⚠️ INCOMPLETE

**Current Responsive Behavior**:
```css
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;  /* Stack columns */
  }
  .preview-column {
    display: none;  /* Hide preview */
  }
}
```

**Issues**:
- Preview column completely hidden on mobile (poor UX)
- No mobile-optimized layout
- Sidebar doesn't adapt for mobile
- Modals may overflow on small screens

**TODO**:
- Implement mobile-friendly preview (maybe tabs or accordion)
- Add hamburger menu for sidebar on mobile
- Test modal on mobile devices
- Add touch-friendly button sizes
- Test on tablets (768px-1024px range)

---

### 11. Accessibility - Not Implemented

**Status**: ⚠️ TODO

**Missing Accessibility Features**:
- No ARIA labels on interactive elements
- No keyboard navigation support
- No focus indicators beyond default
- No screen reader support
- Color contrast not verified for WCAG compliance

**TODO**:
- Add ARIA attributes (`aria-label`, `aria-describedby`, etc.)
- Implement keyboard navigation (Tab, Enter, Escape)
- Add visible focus indicators
- Test with screen readers
- Verify color contrast ratios
- Add skip-to-content link

---

### 12. Performance - No Optimization

**Status**: ⚠️ TODO

**Current State**:
- No code splitting
- No lazy loading of components
- No memoization (except PreviewColumn's useMemo)
- All assets loaded on initial page load

**TODO**:
- Implement React.lazy() for modal and preview components
- Add code splitting by route (when routes added)
- Memoize expensive renders with React.memo
- Optimize image loading (lazy load, WebP format)
- Add loading skeletons for better perceived performance

---

## Summary of Key Findings

### ✅ Implemented & Working

1. **Core Functionality**:
   - Post generation with customizable tone and style
   - LinkedIn OAuth integration
   - Post approval and revision workflow
   - Real-time preview
   - Image generation toggle
   - Multi-agent toggle

2. **API Integration**:
   - All 5 API endpoints properly implemented
   - Type-safe API layer
   - Error handling in place

3. **UI/UX**:
   - Glassmorphism design system
   - Animated gradient background
   - Responsive layout (basic)
   - Toast notifications
   - Loading states

4. **Developer Experience**:
   - TypeScript strict mode
   - Component modularity
   - Path aliases (@/)
   - Hot module replacement (Vite)

### ⚠️ Placeholders & TODOs

1. **Navigation**: History, Scheduled, Settings pages not implemented
2. **Post Type**: Hardcoded to "ai_news"
3. **Profile Data**: Mock LinkedIn profile in preview
4. **Error Handling**: No retry logic
5. **Validations**: Incomplete form validation
6. **Mobile**: Incomplete responsive design
7. **Accessibility**: No ARIA or keyboard support
8. **Performance**: No optimization techniques

### 🔧 Backend Dependencies

The frontend expects the backend to provide:

1. **User ID Persistence**: Backend must generate and return `user_id` after OAuth
2. **Session Management**: Backend must maintain session state by `session_id`
3. **Image Storage**: Backend must serve images at `/images/*` endpoint
4. **Token Storage**: Backend must store and manage LinkedIn OAuth tokens
5. **Revision Logic**: Backend must handle revision requests and regenerate content

---

## Quick Reference for AI Agents

### To Add a New Form Field:

1. Add state in `App.tsx`
2. Create component in `src/components/editor/`
3. Add to `PostRequest` type in `src/types/index.ts`
4. Update form submission in `App.tsx:handleSubmit()`
5. Add to backend API payload

### To Add a New API Endpoint:

1. Add endpoint to `src/config/api.ts:API_ENDPOINTS`
2. Add proxy config in `vite.config.ts` if needed
3. Create types in `src/types/index.ts`
4. Create service function in `src/services/`
5. Call from component

### To Add a New Component:

1. Create component file in appropriate `src/components/` subdirectory
2. Export from `index.ts` in that subdirectory
3. Import in parent component
4. Add TypeScript types for props

### To Modify Styling:

1. Update CSS custom properties in `src/index.css` (lines 10-58)
2. Use existing design tokens for consistency
3. Follow glassmorphism pattern for new components
4. Test dark theme compatibility

---

**End of Documentation**

*For questions or updates, refer to conversation history or codebase.*
