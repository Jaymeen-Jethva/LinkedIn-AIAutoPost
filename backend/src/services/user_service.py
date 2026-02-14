from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from datetime import datetime
import uuid

from src.framework.db_schema import User, Credential


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """Find user by email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user_with_mock_credentials(self, email: str, full_name: str) -> User:
        """Create user and generate mock LinkedIn credentials"""
        # Check if exists
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
             return existing_user
             
        # Create User
        new_user = User(email=email, full_name=full_name)
        self.db.add(new_user)
        await self.db.flush()
        
        # Mock Creds
        mock_cred = Credential(
            user_id=new_user.id,
            linkedin_person_id=f"mock_{uuid.uuid4().hex[:8]}",
            access_token=f"mock_token_{uuid.uuid4().hex}",
            token_expires_at=int(datetime.now().timestamp()) + 31536000, # 1 year
            scope="openid profile w_member_social email"
        )
        self.db.add(mock_cred)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_linkedin_id(self, linkedin_person_id: str) -> User | None:
        """Find a user based on their linked LinkedIn ID"""
        # Query Credential first since it has the index
        stmt = select(Credential).where(Credential.linkedin_person_id == linkedin_person_id)
        result = await self.db.execute(stmt)
        credential = result.scalar_one_or_none()
        
        if credential:
            # Fetch the associated user
            # We could use joinedload option in the query above for efficiency
            # But for now, simple get is fine
            stmt_user = select(User).where(User.id == credential.user_id)
            result_user = await self.db.execute(stmt_user)
            return result_user.scalar_one_or_none()
        return None

    async def create_user_with_linkedin(self, 
                                      linkedin_person_id: str, 
                                      access_token: str, 
                                      expires_in: int,
                                      email: str = None, 
                                      full_name: str = None, 
                                      avatar_url: str = None) -> User:
        """Create a new user and link their LinkedIn credentials"""
        
        # 1. Create User
        new_user = User(
            email=email,
            full_name=full_name,
            avatar_url=avatar_url
        )
        self.db.add(new_user)
        await self.db.flush()  # Flush/Commit to get the ID
        
        # 2. Create Credential
        new_credential = Credential(
            user_id=new_user.id,
            linkedin_person_id=linkedin_person_id,
            access_token=access_token,
            token_expires_at=int(datetime.now().timestamp()) + expires_in,
            scope="openid profile w_member_social email"
        )
        self.db.add(new_credential)
        
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_linkedin_credentials(self, 
                                        user_id: str, 
                                        access_token: str, 
                                        expires_in: int) -> None:
        """Update existing credentials for a user"""
        stmt = update(Credential).where(Credential.user_id == user_id).values(
            access_token=access_token,
            token_expires_at=int(datetime.now().timestamp()) + expires_in,
            updated_at=datetime.utcnow()
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_credentials(self, user_id: str) -> Credential | None:
        """Get LinkedIn credentials for a specific user"""
        stmt = select(Credential).where(Credential.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def remove_linkedin_credentials(self, user_id: str) -> None:
        """Remove LinkedIn credentials for a specific user"""
        stmt = select(Credential).where(Credential.user_id == user_id)
        result = await self.db.execute(stmt)
        credential = result.scalar_one_or_none()
        
        if credential:
            await self.db.delete(credential)
            await self.db.commit()
