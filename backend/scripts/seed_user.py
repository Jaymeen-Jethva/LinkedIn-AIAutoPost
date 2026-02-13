import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.clients.sqlite_client import get_db_context, init_db
from src.framework.db_schema import User, Credential
from sqlalchemy.future import select

async def seed_test_user():
    print("🌱 Seeding test user...")
    
    # Ensure tables exist
    await init_db()
    
    async with get_db_context() as db:
        # Check if test user already exists
        stmt = select(User).where(User.email == "test@example.com")
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ Test user already exists: {user.id}")
            # Ensure credentials exist
            stmt_cred = select(Credential).where(Credential.user_id == user.id)
            result_cred = await db.execute(stmt_cred)
            cred = result_cred.scalar_one_or_none()
            
            if not cred:
                print("⚠️ User exists but missing credentials. Creating mock credentials...")
                # Create mock credential
                mock_cred = Credential(
                    user_id=user.id,
                    linkedin_person_id="mock_person_id_12345",
                    access_token="mock_access_token_xyz",
                    token_expires_at=int(datetime.now().timestamp()) + 3600 * 24 * 60, # 60 days
                    scope="openid profile w_member_social email"
                )
                db.add(mock_cred)
                await db.commit()
                print("✅ Mock credentials created.")
            
            print(f"\n📋 Use this User ID for testing: {user.id}")
            return user.id
            
        else:
            print("Creating new test user...")
            # Create User
            new_user = User(
                email="test@example.com",
                full_name="Test User",
                avatar_url="https://example.com/avatar.jpg"
            )
            db.add(new_user)
            await db.flush()
            
            # Create Credential
            mock_cred = Credential(
                user_id=new_user.id,
                linkedin_person_id="mock_person_id_12345",
                access_token="mock_access_token_xyz",
                token_expires_at=int(datetime.now().timestamp()) + 3600 * 24 * 60, # 60 days
                scope="openid profile w_member_social email"
            )
            db.add(mock_cred)
            await db.commit()
            await db.refresh(new_user)
            
            print(f"✅ Created test user: {new_user.full_name}")
            print(f"\n📋 Use this User ID for testing: {new_user.id}")
            return new_user.id

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed_test_user())
