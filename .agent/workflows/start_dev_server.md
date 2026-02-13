---
description: Start the backend and frontend development servers
---

1. Start the backend
// turbo
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd 'f:\UPGRADDDDDDD STUDY\MY PROJECTS\LinkedInAIAutoPost\backend'; .venv\Scripts\activate; python -m uvicorn app.main:app --port 8000 --reload"

2. Start the frontend
// turbo
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd 'f:\UPGRADDDDDDD STUDY\MY PROJECTS\LinkedInAIAutoPost\frontend'; npm run dev"
