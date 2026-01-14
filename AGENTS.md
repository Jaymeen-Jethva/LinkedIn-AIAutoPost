# LinkedIn AI AutoPost - Agent Guidelines (`AGENTS.md`)

> **CRITICAL**: This document defines the **STRICT** operational rules for this repository. All AI agents and human developers MUST follow these guidelines to maintain the integrity of the refactored architecture.

## 1. 🏗️ Project Context & Architecture

This is a **Python 3.11+ FastAPI** backend with a **React + Vite** frontend.
The backend follows a **Modular Monolith** architecture with strict separation of concerns.

### Directory Structure Requirements
Code MUST be placed in specific directories based on its function. **DO NOT** create files in the root `backend/` directory (except config).

```
backend/app/
├── main.py              # Entry point & Route Aggregation ONLY
├── api/                 # Routers (Controllers) - Request/Response handling ONLY
├── models/              # Pydantic Models - Data Contracts
├── services/            # Business Logic - content generation, workflow
├── clients/             # External Integrations - DB, LinkedIn, Tokens
└── tools/               # Functional Tools - Search, Utilities
```

---

## 2. ⚡ Local Development Commands

All commands should be run from the `backend/` directory unless specified.

### setup & Install
```bash
# Create virtual environment (Python 3.11)
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Server
**Standard Command:**
```bash
python -m uvicorn app.main:app --port 8000 --reload
```

### Linting & Formatting
Agents should assume standard Python tooling is desired even if not explicitly installed yet.
```bash
# formatting
black app tests
# linting
ruff check app
# type checking
mypy app
```

---

## 3. 🛡️ Strict Architectural Rules

**Rule #1: Route/Logic Separation**
*   **Routers (`app/api/`)** MUST NOT contain business logic.
*   Routers should ONLY:
    1.  Receive Request
    2.  Validate Input (via Pydantic)
    3.  Call Service
    4.  Return Response
*   Violations: Writing `requests.get()` or complex `if/else` logic inside a router function.

**Rule #2: Service Layer Isolation**
*   All business logic belongs in `app/services/`.
*   Services should be pure Python classes/functions where possible.
*   Services should NOT rely on `FASTAPI.Request` or `FASTAPI.Response` objects.

**Rule #3: Model Organization**
*   **DO NOT** create a single massive `models.py`.
*   Create separate model files for each domain/router (e.g., `linkedin_models.py`, `post_models.py`).
*   Request models (`*Request`) and Response models (`*Response`) must be clearly explicit.

**Rule #4: Configuration**
*   **NEVER** hardcode secrets or API keys.
*   ALWAYS use `os.getenv()` or `python-dotenv` which is loaded in `app/main.py`.
*   Config files stay in `backend/` root (`.env`).

---

## 4. 🎨 Code Style Guidelines

### 4.1 Imports
*   **Absolute Imports ONLY**: Use `from app.services.xyz import ...`
*   **NO** Relative imports (e.g., `from ..services import ...`).
*   Group imports: Standard Lib -> Third Party -> Local Application.

### 4.2 Typing (Python 3.11+)
*   **Generic Types**: Use built-in generics.
    *   ✅ `list[str]`, `dict[str, Any]`
    *   ❌ `List[str]`, `Dict[str, Any]` (from `typing`)
*   **Optional**: Use `|` syntax where appropriate or `Optional`.
    *   ✅ `str | None`
    *   ✅ `Optional[str]`
*   **Return Types**: ALL functions must have return type annotations.

```python
def calculate_metrics(data: dict[str, int]) -> float:
    ...
```

### 4.3 Naming Conventions
*   **Files**: `snake_case.py` (e.g., `linkedin_service.py`)
*   **Classes**: `PascalCase` (e.g., `LinkedInService`)
*   **Functions/Variables**: `snake_case` (e.g., `get_user_profile`)
*   **Constants**: `UPPER_CASE` (e.g., `MAX_RETRY_COUNT`)

### 4.4 Error Handling
*   Use `fastapi.HTTPException` in Routers.
*   Use standard Python exceptions (`ValueError`, `RuntimeError`) in Services.
*   **Catch Specific Exceptions**: Never use bare `except:`.

**Example Pattern:**
```python
# Service
def get_data() -> dict:
    if not found:
        raise ValueError("Item not found")

# Router
try:
    data = service.get_data()
except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

---

## 5. 🤖 Working with AI/LLMs

When implementing AI features (Gemini, etc.):
1.  **Fail Gracefully**: AI services fail. Always implement `try/except` and fallback logic.
2.  **Retry Logic**: Use `tenacity` library for all external API calls.
3.  **Prompt Engineering**: Keep prompts in the Service layer or a dedicated `prompts.py` file. Do not bury prompts in logic code.

## 6. Frontend Integration

*   **CORS**: Ensure `CORSMiddleware` in `main.py` includes the frontend URL.
*   **JSON Response**: Always return valid JSON. Avoid returning raw strings unless debugging.
*   **Static Files**: The backend does NOT serve frontend static files. Frontend is separate (Vite).

---

## 7. Migration & Refactoring Maintenance

If you (the Agent) are asked to add a new feature:
1.  **Check `AGENTS.md`** first.
2.  **Plan**: Identify which Router, Model, and Service needs updates.
3.  **Implement**:
    *   Create Pydantic Model (`app/models/new_feature.py`)
    *   Create Service Logic (`app/services/new_service.py`)
    *   Create Endpoint (`app/api/new_router.py`)
    *   Register Router in `app/main.py`
4.  **Verify**: Run the server and check endpoints.

## 8. 💾 Database Operations (Strict)

**Rule #1: Async Only**
*   Use `sqlalchemy.ext.asyncio` for all DB interactions.
*   NEVER use synchronous IO in async endpoints (e.g., standard `sqlite3` or sync SQLAlchemy sessions).

**Rule #2: Service Layer Abstraction**
*   **Routers** must NEVER write raw SQL or complex ORM queries.
*   Delegate all DB access to a Service class (e.g., `UserService`, `PostService`).
*   Example Router:
    ```python
    # ✅ Correct
    user = await user_service.get_user(user_id)
    
    # ❌ Incorrect
    result = await db.execute(select(User).where(User.id == user_id))
    ```

**Rule #3: Migrations**
*   **NEVER** modify `db_models.py` without creating a migration.
*   **Workflow**:
    1.  Modify `app/models/db_models.py`
    2.  Run `python -m alembic revision --autogenerate -m "description"`
    3.  Run `python -m alembic upgrade head`

**Rule #4: Session Dependency**
*   Use `db: AsyncSession = Depends(get_db)` in routers.
*   Pass this session explicitly to Service classes: `UserService(db)`.

**Rule #5: Stateless Services**
*   Services should NOT hold state (like `self.access_token`).
*   Pass required IDs/Tokens as method arguments.
*   Exception: `self.db` session is allowed in `__init__`.

