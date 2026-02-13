# Agent Development Guide - LinkedIn AI AutoPost Backend

**Last Updated:** 2026-02-14  
**Architecture Version:** 2.0 (Post-Refactoring)

This document guides AI agents working on this codebase. Follow these conventions to maintain consistency and quality.

---

## Architecture Overview

```
src/
├── controller/          # HTTP request handlers (FastAPI routers)
├── framework/           # Core infrastructure (config, exceptions, validators)
├── services/            # Business logic layer
│   ├── ai/             # LangGraph workflows & Gemini services
│   ├── linkedin/       # LinkedIn OAuth & API services
│   ├── post_service.py # Post CRUD operations
│   └── user_service.py # User & credential management
├── models/             # Pydantic models (API request/response schemas)
├── clients/            # External service clients (database)
├── tools/              # Utility functions (Tavily search)
└── main.py             # FastAPI application entry point
```

---

## Core Principles

### SOLID Principles
- **Single Responsibility**: Each service/class has ONE clear purpose
- **Open/Closed**: Extend via new classes, not modifying existing ones
- **Liskov Substitution**: Use base classes/protocols for polymorphism
- **Interface Segregation**: Keep interfaces focused and minimal
- **Dependency Inversion**: Depend on abstractions (framework layer), not concretions

### DRY (Don't Repeat Yourself)
- **Validation**: Use `framework.validators` (PostValidator, OAuthValidator)
- **Configuration**: Use `framework.settings` singleton
- **Exceptions**: Use `framework.exceptions` custom hierarchy
- **Never**: Duplicate validation logic across controllers
- **Never**: Use `os.getenv()` directly - use `settings` instead

---

## Framework Layer (`src/framework/`)

The foundation of all services. **Always import from here first.**

### `config.py` - Centralized Configuration
```python
from src.framework import settings

# ✅ Correct
gemini_api_key = settings.GEMINI_API_KEY
max_retries = settings.MAX_RETRIES

# ❌ Wrong
import os
gemini_api_key = os.getenv("GEMINI_API_KEY")  # DON'T DO THIS
```

**Available Settings:**
- Database: `DATABASE_URL`, `DB_ECHO`
- LinkedIn OAuth: `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REDIRECT_URI`
- Gemini: `GEMINI_API_KEY`, `GEMINI_FAST_MODEL`, `GEMINI_POWERFUL_MODEL`, `GEMINI_IMAGE_MODEL`
- Retry: `MAX_RETRIES`, `RETRY_MIN_WAIT`, `RETRY_MAX_WAIT`
- Workflow: `MAX_REVISIONS`
- App: `FRONTEND_URL`, `DEBUG`

**Adding New Settings:**
1. Add field to `Settings` class in `config.py`
2. Use Pydantic `Field()` with description and default
3. Update `.env.example` with new variable

### `exceptions.py` - Error Handling
```python
from src.framework import ValidationError, ExternalServiceError

# ✅ Correct - Raise appropriate exception
if not topic.strip():
    raise ValidationError("Topic cannot be empty")

# For external API failures
try:
    response = requests.post(linkedin_api_url)
except requests.RequestException as e:
    raise ExternalServiceError("LinkedIn", f"API call failed: {e}")
```

**Exception Types:**
- `ValidationError` (400) - Input validation failures
- `AuthenticationError` (401) - Missing/invalid credentials
- `AuthorizationError` (403) - Permission denied
- `ResourceNotFoundError` (404) - Entity not found
- `ExternalServiceError` (502) - Third-party API failures
- `WorkflowError` (500) - LangGraph workflow issues
- `ConfigurationError` (500) - Missing environment variables

### `validators.py` - Input Validation
```python
from src.framework import PostValidator, OAuthValidator

# ✅ Correct - Reuse validators
topic = PostValidator.validate_topic(request.topic)
post_type = PostValidator.validate_post_type(request.post_type)

# ❌ Wrong - Inline validation
if len(topic) < 5:  # DON'T DUPLICATE THIS LOGIC
    raise HTTPException(...)
```

---

## Service Layer Organization

### AI Services (`src/services/ai/`)

**When to modify:**
- Adding new LangGraph workflows
- Updating Gemini prompts
- Changing multi-agent orchestration
- Modifying AI model configurations

**Files:**
- `gemini_client.py` - Direct Gemini API calls, retry logic
- `workflow_manager.py` - LinkedIn post generation workflow (LangGraph)
- `agent_orchestrator.py` - Multi-agent system orchestration
- `agents.py` - Individual agent classes (Research, Strategy, Writer, etc.)

**Key Patterns:**
```python
# Always use settings for models
response = client.models.generate_content(
    model=settings.GEMINI_FAST_MODEL,  # ✅ From config
    contents=prompt
)

# Use retry decorator for external calls
@gemini_retry()
def _generate_with_retry(model: str, prompt: str):
    return client.models.generate_content(...)

# Raise appropriate exceptions
try:
    result = await llm.ainvoke(prompt)
except Exception as e:
    raise WorkflowError(f"Agent execution failed: {e}")
```

### LinkedIn Services (`src/services/linkedin/`)

**When to modify:**
- Updating OAuth flow
- Adding LinkedIn API endpoints
- Modifying authentication logic

**Files:**
- `oauth_service.py` - OAuth 2.0 flow (authorization URL, token exchange, user info)
- `api_client.py` - LinkedIn REST API calls (posting, profile)

**Key Patterns:**
```python
# OAuth service should handle all LinkedIn auth
oauth_service = LinkedInOAuthService()
auth_url, state = oauth_service.generate_authorization_url()

# Always set timeouts for external calls
response = requests.get(url, headers=headers, timeout=10)

# Raise ExternalServiceError for API failures
except requests.exceptions.RequestException as e:
    raise ExternalServiceError("LinkedIn", f"API call failed: {e}")
```

### Core Services

**`post_service.py`** - Post CRUD operations
- Create, read, update, delete posts
- Database transactions
- Uses `framework.db_schema` models

**`user_service.py`** - User & credential management
- User creation/lookup
- LinkedIn credential storage
- Uses `framework.db_schema` models

---

## Controller Layer (`src/controller/`)

**Purpose:** Handle HTTP requests, validate input, call services, return responses

**Anti-patterns to avoid:**
- ❌ Business logic in controllers
- ❌ Direct database access
- ❌ OAuth logic inline
- ❌ Validation logic inline

**Correct pattern:**
```python
from src.framework import PostValidator, ValidationError
from src.services.ai import LinkedInWorkflow

@router.post("/generate")
async def generate_post(request: PostRequest, db: AsyncSession = Depends(get_db)):
    # 1. Validate input using framework
    try:
        topic = PostValidator.validate_topic(request.topic)
        post_type = PostValidator.validate_post_type(request.post_type)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    
    # 2. Call service layer
    workflow = LinkedInWorkflow(db, request.user_id)
    result = await workflow.generate_post(topic, post_type)
    
    # 3. Return response
    return result
```

---

## Database Layer (`src/framework/db_schema.py`)

**SQLAlchemy Models:**
- `User` - User accounts
- `Credential` - LinkedIn OAuth tokens
- `Post` - Generated posts

**When to modify:**
- Adding new database tables
- Adding columns to existing tables
- Changing relationships

**Migration Process:**
1. Update model in `db_schema.py`
2. Create Alembic migration: `alembic revision --autogenerate -m "description"`
3. Review migration in `alembic/versions/`
4. Apply migration: `alembic upgrade head`

---

## When to Use Which SKILL

### `@[.agent/skills/executing-plans]`

**Use when:**
- Implementing a multi-phase refactoring plan
- Making changes across many files
- Need checkpoints for user review between batches

**Pattern:**
1. Load and review implementation plan
2. Execute tasks in batches (5-10 files per batch)
3. Commit after each batch
4. Report progress with `notify_user` between batches
5. Final walkthrough after completion

**Example:** The refactoring we just completed (8 phases, 7 commits, multiple batches)

### `@[.agent/skills/langchain-architecture]`

**Use when:**
- Building/modifying LangGraph workflows (`services/ai/workflow_manager.py`)
- Creating new AI agents (`services/ai/agents.py`)
- Implementing multi-agent systems (`services/ai/agent_orchestrator.py`)
- Adding LangChain tools or memory systems
- Debugging LLM invocation issues

**Key Patterns from Skill:**
- Use `create_react_agent` for ReAct agents
- Use `StateGraph` for custom workflows
- Use `MemorySaver` for conversation persistence
- Always use async methods (`ainvoke`, `astream`)
- Implement proper error handling for LLM calls

**Example:** Modifying the multi-agent LinkedIn post generation system

### `@[.agent/skills/test-driven-development]`

**Use when:**
- Adding new features that need tests
- Refactoring code with test coverage
- Fixing bugs with test-first approach

**Pattern:**
1. Write failing test first
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. Add integration tests for critical paths

**Example:** Adding tests for `LinkedInOAuthService` or `PostValidator`

---

## Coding Standards

### Import Order
```python
# 1. Standard library
import os
import json
from typing import Dict, List

# 2. Third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

# 3. Framework (always import from framework first)
from src.framework import settings, ValidationError, PostValidator

# 4. Local services
from src.services.ai import LinkedInWorkflow
from src.services.user_service import UserService
```

### Naming Conventions
- **Classes:** `PascalCase` (LinkedInOAuthService, PostValidator)
- **Functions/Methods:** `snake_case` (generate_post, validate_topic)
- **Constants:** `UPPER_SNAKE_CASE` (MAX_RETRIES, GEMINI_FAST_MODEL)
- **Private:** Prefix with `_` (_generate_with_retry)

### Type Hints
Always use type hints for function signatures:
```python
async def generate_post(
    topic: str,
    post_type: str,
    include_image: bool = True
) -> LinkedInPost:
    ...
```

### Docstrings
Use Google-style docstrings:
```python
def generate_authorization_url(self) -> Tuple[str, str]:
    """
    Generate LinkedIn OAuth authorization URL with CSRF protection.
    
    Returns:
        Tuple of (authorization_url, state_token)
        
    Raises:
        ValidationError: If OAuth is not configured
    """
```

---

## Common Development Tasks

### Adding a New API Endpoint
1. Add route to appropriate controller (`src/controller/`)
2. Use framework validators for input validation
3. Call service layer for business logic
4. Return Pydantic model response
5. Add to FastAPI docs with proper descriptions

### Adding a New Service
1. Create in appropriate domain (`ai/`, `linkedin/`, or root)
2. Import from `framework` for config/exceptions
3. Add to `services/__init__.py` exports
4. Follow Single Responsibility Principle

### Modifying LangGraph Workflows
1. Use `@[.agent/skills/langchain-architecture]` skill
2. Update state schema if needed
3. Test with small inputs first
4. Add logging for each workflow step
5. Handle LLM errors with `WorkflowError`

### Adding Configuration
1. Add to `framework/config.py` Settings class
2. Update `.env.example`
3. Use throughout codebase via `settings.YOUR_VAR`

---

## Testing Guidelines

### Unit Tests
- Test validators independently
- Mock external services (Gemini, LinkedIn)
- Test exception handling

### Integration Tests
- Test full API endpoints
- Use test database
- Test LangGraph workflows end-to-end

### Manual Testing Checklist
- [ ] Start server: `uvicorn src.main:app --reload --port 8000`
- [ ] Check health: `GET /health`
- [ ] Test OAuth flow: `/linkedin/connect` → `/linkedin/callback`
- [ ] Generate post: `POST /generate-post`
- [ ] Verify database persistence

---

## Deployment Considerations

- All configuration via environment variables (`.env`)
- Database migrations via Alembic
- LangGraph workflows may need separate worker processes
- LinkedIn OAuth requires HTTPS in production

---

## Troubleshooting

**Import errors after refactoring:**
- Ensure using `from src.*` (not `from app.*`)
- Check `__init__.py` exports

**Configuration errors:**
- Verify `.env` file exists
- Check `settings` has required fields
- Use `ConfigurationError` for missing env vars

**LangGraph workflow failures:**
- Check LangSmith traces (if enabled)
- Add logging to each workflow node
- Verify agent state schema matches workflow

**External API failures:**
- Always use timeouts (10s recommended)
- Wrap with `ExternalServiceError`
- Implement retry logic for transient failures

---

## Quick Reference

**Framework imports:**
```python
from src.framework import (
    settings, ValidationError, ExternalServiceError,
    PostValidator, OAuthValidator
)
```

**Service imports:**
```python
from src.services.ai import LinkedInWorkflow, MultiAgentGeminiWorkflow
from src.services.linkedin import LinkedInOAuthService
```

**Never:**
- Use `os.getenv()` - use `settings` instead
- Duplicate validation - use validators
- Inline OAuth logic - use `LinkedInOAuthService`
- Hardcode API URLs - use `settings`

---

**For questions or clarifications, refer to:**
- `implementation_plan.md` - Original refactoring plan
- `walkthrough.md` - Completed refactoring documentation
- `.agent/skills/` - Skill-specific guidance
