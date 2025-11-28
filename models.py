from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    platform: str = Field(default="linkedin")
    title: Optional[str] = None
    text_content: str
    image_url: Optional[str] = None  # Renamed from image_path
    scheduled_at: datetime
    status: str = Field(default="scheduled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
