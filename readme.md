# 🚀 LinkedIn AI Post Automation

<div align="center">
  <p><strong>Generate stunning LinkedIn posts with AI-powered content and images</strong></p>
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge&logo=fastapi" alt="Status">
  <img src="https://img.shields.io/badge/AI-Gemini-blue?style=for-the-badge&logo=google" alt="AI">
  <img src="https://img.shields.io/badge/UI-Glassmorphism-purple?style=for-the-badge" alt="UI">
</div>

---

## ✨ Overview

An intelligent LinkedIn automation system that uses **Google Gemini AI** to generate personalized, engaging posts with AI-created images. Features a modern **glassmorphism UI** and workflow orchestration using **LangGraph**.

### 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🤖 AI-Powered Content | Generate professional LinkedIn posts using Gemini 2.5 Pro |
| 🔍 Web Search | Latest information via Tavily search integration |
| 🎨 Smart Images | AI-generated visuals with Gemini 2.0 Flash |
| 🔄 Approval Workflow | Review and revise content before posting |
| 🔗 LinkedIn OAuth | Connect your account directly from the UI |
| 🌙 Dark/Light Theme | Beautiful glassmorphism interface |

---

## 🛠️ Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key
- LinkedIn Developer App (for real posting)

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd linkedin-ai-autopost
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: For enhanced content
TAVILY_API_KEY=your_tavily_api_key_here

# Required for LinkedIn posting
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
```

> **Note**: Get LinkedIn credentials from [LinkedIn Developers](https://www.linkedin.com/developers/). Add `http://localhost:8000/linkedin/callback` to your app's Authorized redirect URLs.

### Run

```bash
python main.py
```

Open **http://localhost:8000** in your browser.

---

## 📖 Usage

1. **Connect LinkedIn** - Click "Connect LinkedIn" button in the header
2. **Enter Topic** - Describe what you want to post about
3. **Select Style** - Choose between AI News or Personal Milestone
4. **Generate** - Click "Generate Post" and wait for AI magic
5. **Review** - Check the preview, request revisions if needed
6. **Post** - Approve to publish directly to LinkedIn

---

## 🏗️ Project Structure

```
linkedin-ai-autopost/
├── main.py                 # FastAPI application (port 8000)
├── gemini_client.py        # Gemini AI integration
├── linkedin_workflow.py    # LangGraph workflow
├── linkedin_api.py         # LinkedIn posting
├── token_storage.py        # OAuth token management
├── tavily_search.py        # Web search integration
├── templates/              # HTML templates
├── static/                 # CSS & JavaScript
└── generated_images/       # AI-generated images
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Web UI |
| `/generate-post` | POST | Generate AI content |
| `/approve-post` | POST | Approve or revise post |
| `/linkedin/connect` | POST | Start OAuth flow |
| `/linkedin/callback` | GET | OAuth callback |
| `/linkedin/status` | GET | Check connection status |
| `/linkedin/disconnect` | POST | Disconnect account |

---

## 🔧 Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |
| `TAVILY_API_KEY` | ❌ | Tavily search API key |
| `LINKEDIN_CLIENT_ID` | ❌ | LinkedIn OAuth Client ID |
| `LINKEDIN_CLIENT_SECRET` | ❌ | LinkedIn OAuth Client Secret |

Without LinkedIn credentials, the app runs in **simulation mode** (posts are logged but not published).

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Gemini API Key not found" | Check `GEMINI_API_KEY` in `.env` |
| "LinkedIn OAuth not configured" | Add `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` to `.env` |
| LinkedIn connection fails | Verify redirect URI is added to your LinkedIn app |
| Images not generating | Check Gemini API quota; fallback image service will be used |
| Port 8000 in use | Kill process: `lsof -ti:8000 \| xargs kill -9` |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
  <p><strong>Built with ❤️ using Google Gemini AI & FastAPI</strong></p>
</div>
