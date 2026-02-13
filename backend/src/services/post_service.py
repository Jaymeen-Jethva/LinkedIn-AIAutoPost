from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from datetime import datetime
from typing import Optional

from src.models.db_models import Post


class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_draft_post(self, 
                              user_id: str, 
                              session_id: str, 
                              topic: str, 
                              post_type: str) -> Post:
        """Create a new post entry in DRAFT status"""
        new_post = Post(
            user_id=user_id,
            session_id=session_id,
            topic=topic,
            post_type=post_type,
            status="DRAFT"
        )
        self.db.add(new_post)
        await self.db.commit()
        await self.db.refresh(new_post)
        return new_post

    async def update_post_content(self, 
                                session_id: str, 
                                content: str, 
                                image_path: Optional[str] = None,
                                image_prompt: Optional[str] = None) -> None:
        """Update the generated content of a post"""
        stmt = update(Post).where(Post.session_id == session_id).values(
            content=content,
            image_path=image_path,
            image_prompt=image_prompt,
            updated_at=datetime.utcnow()
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def mark_as_posted(self, session_id: str, linkedin_urn: str) -> None:
        """Mark post as successfully posted to LinkedIn"""
        stmt = update(Post).where(Post.session_id == session_id).values(
            status="POSTED",
            linkedin_post_urn=linkedin_urn,
            updated_at=datetime.utcnow()
        )
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def get_post_by_session(self, session_id: str) -> Post | None:
        """Retrieve a post by its session ID"""
        stmt = select(Post).where(Post.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
