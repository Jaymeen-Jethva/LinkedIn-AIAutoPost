from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
import uuid

from src.framework.base import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)  # From LinkedIn if available
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    credential = relationship("Credential", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="user")


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    linkedin_person_id = Column(String, unique=True, index=True, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_expires_at = Column(Integer, nullable=True)  # Seconds remaining or timestamp
    scope = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="credential")


class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, index=True, nullable=False)
    
    topic = Column(Text, nullable=False)
    post_type = Column(String, nullable=False)  # AI_NEWS, PERSONAL_MILESTONE
    content = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)
    image_prompt = Column(Text, nullable=True)
    
    status = Column(String, default="DRAFT")  # DRAFT, APPROVED, POSTED, FAILED
    linkedin_post_urn = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="posts")
