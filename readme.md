# 🚀 LinkedIn Post Automation Using AI

<div align="center">
  <p><strong>Generate stunning LinkedIn posts with AI-powered content and images</strong></p>
  <img src="https://img.shields.io/badge/Backend-FastAPI-success?style=for-the-badge&logo=fastapi" alt="Backend">
  <img src="https://img.shields.io/badge/Frontend-React_Vite-blue?style=for-the-badge&logo=react" alt="Frontend">
  <img src="https://img.shields.io/badge/AI-Gemini-blue?style=for-the-badge&logo=google" alt="AI">
</div>

---

## ✨ Overview

An intelligent LinkedIn automation system that uses **Google Gemini AI** to generate personalized, engaging posts with AI-created images. 

**New Architecture:**
- **Backend**: Robust Python FastAPI service handling AI generation, LinkedIn OAuth, and workflow orchestration.
- **Frontend**: Modern React + Vite application (Glassmorphism UI) for a premium user experience.

### 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🤖 AI-Powered Content | Generate professional LinkedIn posts using Gemini 2.5 Pro |
| 🔍 Web Search | Latest information via Tavily search integration |
| 🎨 Smart Images | AI-generated visuals with Gemini 2.0 Flash |
| 🔄 Approval Workflow | Review and revise content before posting |
| 🔗 LinkedIn OAuth | Connect your account directly from the UI |
| 📦 Modular Design | Scalable architecture with separated API, Models, and Services |

---

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Google Gemini API Key
- LinkedIn Developer App (for real posting)

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Configuration (.env):**
Create `backend/.env` file:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: For enhanced content
TAVILY_API_KEY=your_tavily_api_key_here

# Required for LinkedIn posting
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/linkedin/callback

# Frontend URL (CORS)
FRONTEND_URL=http://localhost:3000
```

**Run Backend:**
```bash
# From root directory
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Server running at `http://localhost:8000` (Swagger UI at `/docs`)

---

### 2. Frontend Setup

```bash
cd frontend
npm install
```

**Run Frontend:**
```bash
npm run dev
```
App running at `http://localhost:3000`

---

## 🏗️ Project Structure

```
LinkedInAIAutoPost/
├── backend/                # Python FastAPI Backend
│   ├── .env                # Environment config
│   ├── app/
│   │   ├── main.py         # App entry point & health check
│   │   ├── api/            # Router endpoints (LinkedIn, Posts)
│   │   ├── models/         # Pydantic data models
│   │   ├── services/       # Business logic (Workflow, Gemini)
│   │   ├── clients/        # External clients (Tokens, DB)
│   │   └── tools/          # AI Tools (Tavily)
│   └── tests/              # Test suite
│
└── frontend/               # React + Vite Frontend
    ├── src/
    ├── public/
    └── package.json
```

## 📖 Usage Flow

1. **Connect LinkedIn** - Click "Connect LinkedIn" on the frontend (OAuth flow).
2. **Enter Topic** - Describe your post idea (e.g., "Future of AI Agents").
3. **Select Style** - AI News or Personal Milestone.
4. **Generate** - Backend workflow orchestrates research, writing, and image generation.
5. **Review** - Preview the content and image in the UI.
6. **Post** - Approve to publish directly to your LinkedIn profile.

---

## 🔧 Configuration Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |
| `LINKEDIN_CLIENT_ID` | ❌ | LinkedIn OAuth Client ID |
| `LINKEDIN_CLIENT_SECRET` | ❌ | LinkedIn OAuth Client Secret |
| `TAVILY_API_KEY` | ❌ | Tavily search API key (optional) |
| `FRONTEND_URL` | ❌ | Allowed CORS origin (default: localhost:3000) |

> **Note**: Without LinkedIn credentials, the app runs in **simulation mode** (logs post to console instead of publishing).
