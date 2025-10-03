# 🚀 LinkedIn AI Post Automation

<div align="center">
  <p><strong>Generate stunning LinkedIn posts with AI-powered content and images</strong></p>
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge&logo=fastapi" alt="Status">
  <img src="https://img.shields.io/badge/AI-Gemini-blue?style=for-the-badge&logo=google" alt="AI">
  <img src="https://img.shields.io/badge/UI-Glassmorphism-purple?style=for-the-badge" alt="UI">
</div>

---

## ✨ Overview

An intelligent LinkedIn automation system that leverages **Google Gemini AI** to generate personalized, engaging posts with AI-created images. Built with a sophisticated workflow orchestration using **LangGraph** and a modern **glassmorphism UI** for an exceptional user experience.

### 🎯 Key Features

- **🤖 AI-Powered Content**: Generate professional LinkedIn posts using Gemini 2.5 Pro
- **🎨 Smart Images**: Create relevant visuals with Gemini 2.0 Flash (nano banana)
- **🔄 Approval Workflow**: Review and revise content before posting
- **🌙 Dark/Light Theme**: Beautiful glassmorphism interface with theme toggle
- **📱 Responsive Design**: Works perfectly on desktop and mobile
- **⚡ Real-time Preview**: See your post as you type
- **🔧 Advanced Options**: Customize tone, style, and preferences

---

## 🛠️ Quick Start

### Prerequisites

- **Python 3.8+**
- **Google Gemini API Key**
- **LinkedIn Account** (optional, for real posting)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin-ai-autopost
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:
   ```env
   # Required: Get from https://makersuite.google.com/app/apikey
   GEMINI_API_KEY=your_gemini_api_key_here

   # Optional: For real LinkedIn posting
   LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
   LINKEDIN_PERSON_ID=your_linkedin_person_id
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Open your browser**

   Navigate to: **http://localhost:5000**

   🎉 You're ready to create amazing LinkedIn posts!

---

## 🎨 User Interface

### Modern Glassmorphism Design
- **Dark Theme**: Charcoal background with electric blue accents
- **Glass Cards**: Transparent cards with backdrop blur effects
- **Circuit Patterns**: Subtle tech-inspired background overlays
- **Smooth Animations**: Professional transitions and micro-interactions

### Two-Column Layout
- **Left Panel**: Input controls and post configuration
- **Right Panel**: Live preview of your generated post
- **Responsive**: Adapts beautifully to all screen sizes

---

## 📖 Usage Guide

### 1. **Choose Your Topic**
   - Enter what you want to post about
   - Be specific for better results
   - Example: "Latest developments in AI and machine learning"

### 2. **Select Post Style**
   - **⚡ Short**: Concise, impactful posts for quick reads
   - **🧠 Technical**: Detailed, informative content for professionals
   - **💬 Engaging**: Conversation-starting posts to build connections

### 3. **Customize (Optional)**
   - Add preferences for tone and style
   - Specify technical level or audience
   - Include specific requirements or constraints

### 4. **Generate & Preview**
   - Click the floating action button to generate
   - Watch the live preview update in real-time
   - See your post exactly as it will appear on LinkedIn

### 5. **Review & Approve**
   - Review the generated content and image
   - Request revisions if needed
   - Approve when satisfied

### 6. **Post to LinkedIn**
   - Automatically posts to your LinkedIn profile
   - Includes generated image and hashtags
   - Confirmation when successfully posted

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Your Google Gemini API key |
| `LINKEDIN_ACCESS_TOKEN` | ❌ | For real LinkedIn posting |
| `LINKEDIN_PERSON_ID` | ❌ | Your LinkedIn profile ID |

### Getting API Keys

#### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy it to your `.env` file

#### LinkedIn API (Optional)
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create an app and get your access token
3. Add to your `.env` file for real posting

---

## 🏗️ Project Architecture

```
linkedin-ai-autopost/
├── 📂 Core AI Components
│   ├── gemini_client.py      # Gemini AI integration
│   └── linkedin_workflow.py  # LangGraph workflow orchestration
├── 📂 API & Web Interface
│   ├── main.py              # FastAPI application
│   ├── linkedin_api.py      # LinkedIn API integration
│   └── templates/           # HTML templates
├── 📂 Static Assets
│   ├── static/
│   │   ├── styles.css       # Glassmorphism styling
│   │   └── app.js           # Interactive functionality
│   └── generated_images/    # AI-generated images
└── 📂 Configuration
    ├── .env                 # Environment variables
    ├── requirements.txt     # Python dependencies
    └── pyproject.toml       # Project configuration
```

### Technology Stack

- **Backend**: FastAPI + Uvicorn
- **AI Engine**: Google Gemini 2.5 Pro & 2.0 Flash
- **Workflow**: LangGraph for state management
- **Frontend**: Vanilla JavaScript + Bootstrap 5
- **Styling**: Custom CSS with glassmorphism effects
- **Deployment**: Standalone with auto-reload

---

## 🎯 Post Types

### ⚡ Short Posts
- **Best for**: Quick updates, announcements, achievements
- **Style**: Concise, punchy, attention-grabbing
- **Length**: 1-2 paragraphs
- **Use case**: Product launches, quick wins, daily insights

### 🧠 Technical Posts
- **Best for**: Deep dives, tutorials, industry insights
- **Style**: Detailed, informative, educational
- **Length**: 3-4 paragraphs with technical details
- **Use case**: Research findings, how-to guides, analysis

### 💬 Engaging Posts
- **Best for**: Community building, discussions, networking
- **Style**: Conversational, question-asking, inclusive
- **Length**: 2-3 paragraphs with calls-to-action
- **Use case**: Opinion pieces, community questions, debates

---

## 🔍 Troubleshooting

### Common Issues

**❌ "Gemini API Key not found"**
- Ensure `GEMINI_API_KEY` is set in your `.env` file
- Verify the API key is valid and has quota remaining

**❌ "LinkedIn posting failed"**
- Check if `LINKEDIN_ACCESS_TOKEN` is correctly set
- Verify your LinkedIn app has the right permissions
- The app works in simulation mode without LinkedIn API

**❌ "Images not generating"**
- Ensure Gemini API has image generation capabilities
- Check your API quota and billing settings
- Images will still work in fallback mode

**❌ "Port 5000 already in use"**
```bash
# Find and kill the process
lsof -ti:5000 | xargs kill -9
# Or use a different port
python main.py --port 8000
```

### Getting Help

1. **Check the logs**: The application provides detailed error messages
2. **Verify environment**: Ensure all required variables are set
3. **Test API keys**: Verify your Gemini API key works independently
4. **Check permissions**: Ensure LinkedIn app has posting permissions

---

## 🚀 Advanced Features

### Live Preview
- See your post update in real-time as you type
- Mock LinkedIn interface for accurate preview
- Character counter with visual progress ring

### Advanced Options
- Custom tone and style preferences
- Technical level specification
- Audience targeting options
- Content length preferences

### Theme Customization
- Beautiful dark/light theme toggle
- Smooth sliding animation
- Glassmorphism effects
- Consistent across all components

---

## 📊 Performance & Limits

- **Content Generation**: ~5-10 seconds per post
- **Image Generation**: ~15-30 seconds per image
- **Rate Limits**: Follow Gemini API quotas
- **Character Limits**: Up to 3000 characters per post
- **File Size**: Images optimized for web delivery

---

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and enhancement requests.

### Development Setup
```bash
git clone <repository-url>
cd linkedin-ai-autopost
pip install -r requirements.txt
python main.py
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
  <p><strong>Built with ❤️ using Google Gemini AI & Modern Web Technologies</strong></p>
  <p>
    <a href="#overview">Overview</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#usage-guide">Usage</a> •
    <a href="#configuration">Configuration</a>
  </p>
</div>
