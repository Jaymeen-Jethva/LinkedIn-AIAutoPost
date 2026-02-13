from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.clients.sqlite_client import get_db
from src.services.user_service import UserService
from src.models.user_models import UserCreateRequest, UserResponse

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(request: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new user with mock LinkedIn credentials for testing"""
    service = UserService(db)
    user = await service.create_user_with_mock_credentials(
        email=request.email,
        full_name=request.full_name
    )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        linkedin_connected=True,
        message="User created with mock credentials"
    )
