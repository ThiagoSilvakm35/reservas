from ninja import Schema
from pydantic import Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ReviewCreateSchema(Schema):
    booking_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class ReviewUpdateSchema(Schema):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewOutSchema(Schema):
    id: int
    booking_id: UUID
    user_id: int
    user_name: str
    provider_id: int
    provider_name: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    has_response: bool

class ReviewResponseCreateSchema(Schema):
    text: str

class ReviewResponseUpdateSchema(Schema):
    text: str

class ReviewResponseOutSchema(Schema):
    id: int
    review_id: int
    text: str
    responded_by_id: int
    responded_by_name: str
    created_at: datetime
    updated_at: datetime

class ProviderRatingsSummarySchema(Schema):
    provider_id: int
    provider_name: str
    average_rating: float
    reviews_count: int
    ratings_distribution: dict  # {1: 5, 2: 10, ...} - contagem de avaliações por nota
    
class ReviewListQuerySchema(Schema):
    provider_id: Optional[int] = None
    min_rating: Optional[int] = Field(default=None, ge=1, le=5)
    max_rating: Optional[int] = Field(default=None, ge=1, le=5)
    with_comments_only: Optional[bool] = False
    page: int = 1
    page_size: int = Field(default=10, le=100) 