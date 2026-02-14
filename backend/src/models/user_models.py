from pydantic import BaseModel, EmailStr, Field

class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, description="User full name")

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    linkedin_connected: bool
    message: str = "User created successfully"
