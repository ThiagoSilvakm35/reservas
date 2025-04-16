from ninja import Schema
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID

class ReportCreateSchema(Schema):
    title: str
    type: str = Field(pattern="^(daily|weekly|monthly|custom)$")
    format: str = Field(pattern="^(html|pdf|excel|csv)$")
    start_date: date
    end_date: date
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Relatório Semanal de Reservas",
                "type": "weekly",
                "format": "excel",
                "start_date": "2023-01-01",
                "end_date": "2023-01-07"
            }
        }

class ReportOutSchema(Schema):
    id: UUID
    title: str
    type: str
    format: str
    start_date: date
    end_date: date
    created_by_id: int
    created_by_name: str
    created_at: datetime
    file: Optional[str] = None
    data: Dict[str, Any]

class ReportFilterSchema(Schema):
    type: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly|custom)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = 1
    page_size: int = Field(default=10, le=100)

class ActivityLogOutSchema(Schema):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    description: str
    ip_address: Optional[str] = None
    timestamp: datetime
    extra_data: Optional[Dict[str, Any]] = None

class ActivityLogFilterSchema(Schema):
    user_id: Optional[int] = None
    action: Optional[str] = Field(default=None, pattern="^(login|logout|failed_login|create|update|delete|export|error)$")
    entity_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = 1
    page_size: int = Field(default=10, le=100)

class DashboardStatsSchema(Schema):
    total_users: int
    total_providers: int
    total_bookings: int
    bookings_by_status: Dict[str, int]  # {'pending': 10, 'confirmed': 20, ...}
    recent_activity: List[ActivityLogOutSchema]

class BookingsByDateSchema(Schema):
    date: date
    count: int

class BookingsByTimeSchema(Schema):
    hour: int
    count: int

class TopProvidersSchema(Schema):
    provider_id: int
    provider_name: str
    bookings_count: int
    average_rating: Optional[float] = None

class DashboardChartsSchema(Schema):
    bookings_by_date: List[BookingsByDateSchema]
    bookings_by_time: List[BookingsByTimeSchema]
    top_providers: List[TopProvidersSchema]
    ratings_distribution: Dict[int, int]  # {1: 5, 2: 10, ...} 