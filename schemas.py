"""
Database Schemas for CatAdvisor

Each Pydantic model represents a collection in MongoDB. The collection name
is the lowercase of the class name (handled by helper utils in the app layer).

These schemas shape the MVP: users, cats, sightings, places, posts, likes,
points/badges, and emergency reports.
"""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl

# -------------------- Core Schemas --------------------

class User(BaseModel):
    email: str = Field(..., description="Email address")
    nickname: str = Field(..., max_length=40)
    avatar_url: Optional[HttpUrl] = None
    bio: Optional[str] = Field(None, max_length=300)
    role: Literal["user", "volunteer", "moderator", "admin"] = "user"
    points: int = 0
    badges: List[str] = []
    is_active: bool = True

class Cat(BaseModel):
    name: Optional[str] = Field(None, description="Name or nickname if known")
    description: Optional[str] = Field(None, max_length=500)
    last_known_lat: Optional[float] = Field(None, ge=-90, le=90)
    last_known_lng: Optional[float] = Field(None, ge=-180, le=180)
    status: Literal["unknown", "sterilized", "adopted", "injured"] = "unknown"
    colony: Optional[str] = Field(None, description="Colony or area name")
    photo_url: Optional[HttpUrl] = None

class Sighting(BaseModel):
    cat_id: Optional[str] = Field(None, description="Associated cat id if known")
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    note: Optional[str] = Field(None, max_length=400)
    photo_url: Optional[HttpUrl] = None
    status: Literal["normal", "urgent"] = "normal"
    created_by: Optional[str] = Field(None, description="User id")
    seen_at: Optional[datetime] = None

class Place(BaseModel):
    name: str
    category: Literal["cat_cafe", "shelter", "colony", "event", "art"]
    description: Optional[str] = Field(None, max_length=600)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    opening_hours: Optional[str] = None
    contact: Optional[str] = None
    website: Optional[HttpUrl] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    rating_count: int = 0

class Post(BaseModel):
    author_id: Optional[str] = None
    text: str = Field(..., max_length=1000)
    photo_url: Optional[HttpUrl] = None
    tags: List[str] = []
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    miao_count: int = 0

class Emergency(BaseModel):
    reporter_id: Optional[str] = None
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    description: str = Field(..., max_length=500)
    photo_url: Optional[HttpUrl] = None
    status: Literal["open", "in_progress", "resolved"] = "open"

class Report(BaseModel):
    reporter_id: Optional[str] = None
    target_type: Literal["post", "cat", "place", "sighting"]
    target_id: str
    reason: Literal["spam", "offensive", "duplicate", "privacy", "other"]
    note: Optional[str] = Field(None, max_length=300)

class Badge(BaseModel):
    code: str = Field(..., description="Unique badge code, e.g., CATOGRAPHER")
    label: str
    description: Optional[str] = None
    icon: Optional[str] = Field(None, description="Icon name reference")

# Minimal editorial content for CMS MVP
class Article(BaseModel):
    title: str
    body: str
    cover_url: Optional[HttpUrl] = None
    author: Optional[str] = None
    tags: List[str] = []
