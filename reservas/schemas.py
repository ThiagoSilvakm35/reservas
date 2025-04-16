from ninja import Schema
from pydantic import Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from uuid import UUID

# Esquemas para Prestadores
class ProviderCreateSchema(Schema):
    service_name: str
    description: Optional[str] = None
    average_service_time: int = Field(default=60, ge=10, le=240)
    interval_between_bookings: int = Field(default=15, ge=0, le=60)
    max_daily_bookings: int = Field(default=10, ge=1, le=100)

class ProviderUpdateSchema(Schema):
    service_name: Optional[str] = None
    description: Optional[str] = None
    average_service_time: Optional[int] = Field(default=None, ge=10, le=240)
    interval_between_bookings: Optional[int] = Field(default=None, ge=0, le=60)
    max_daily_bookings: Optional[int] = Field(default=None, ge=1, le=100)
    active: Optional[bool] = None

class ProviderOutSchema(Schema):
    id: int
    user_id: int
    user_name: str
    user_email: str
    service_name: str
    description: Optional[str] = None
    average_service_time: int
    interval_between_bookings: int
    max_daily_bookings: int
    active: bool
    created_at: datetime
    updated_at: datetime

# Esquemas para Disponibilidade
class ProviderAvailabilityCreateSchema(Schema):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    is_available: bool = True
    
    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('A hora de término deve ser posterior à hora de início')
        return v

class ProviderAvailabilityUpdateSchema(Schema):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None

class ProviderAvailabilityOutSchema(Schema):
    id: int
    provider_id: int
    day_of_week: int
    day_name: str  # Nome do dia da semana
    start_time: time
    end_time: time
    is_available: bool

# Esquemas para Pausas
class ProviderBreakCreateSchema(Schema):
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None
    
    @validator('end_datetime')
    def end_datetime_after_start_datetime(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('O fim da pausa deve ser posterior ao início')
        return v

class ProviderBreakUpdateSchema(Schema):
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    reason: Optional[str] = None

class ProviderBreakOutSchema(Schema):
    id: int
    provider_id: int
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None

# Esquemas para Reservas
class BookingCreateSchema(Schema):
    provider_id: int
    start_datetime: datetime
    notes: Optional[str] = None
    
    @validator('start_datetime')
    def start_datetime_not_in_past(cls, v):
        if v < datetime.now():
            raise ValueError('A data de início não pode estar no passado')
        return v

class BookingUpdateSchema(Schema):
    start_datetime: Optional[datetime] = None
    notes: Optional[str] = None

class BookingStatusUpdateSchema(Schema):
    status: str = Field(pattern="^(pending|confirmed|canceled|completed)$")

class BookingOutSchema(Schema):
    id: UUID
    user_id: int
    user_name: str
    provider_id: int
    provider_name: str
    start_datetime: datetime
    end_datetime: datetime
    status: str
    confirmation_code: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    has_review: bool

# Esquemas para Lista de Espera
class WaitingListCreateSchema(Schema):
    provider_id: int
    desired_date: date
    time_preference: Optional[str] = None

class WaitingListOutSchema(Schema):
    id: int
    user_id: int
    user_name: str
    provider_id: int
    provider_name: str
    desired_date: date
    time_preference: Optional[str] = None
    created_at: datetime
    is_notified: bool

# Esquemas para horários disponíveis
class AvailableTimeslotSchema(Schema):
    start_time: datetime
    end_time: datetime
    is_available: bool

class AvailableTimeslotsQuerySchema(Schema):
    provider_id: int
    date: date

class AvailableTimeslotsResponseSchema(Schema):
    provider_id: int
    provider_name: str
    date: date
    timeslots: List[AvailableTimeslotSchema]
    
# Esquemas para exportação
class ExportBookingsQuerySchema(Schema):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    provider_id: Optional[int] = None
    status: Optional[str] = Field(default=None, pattern="^(pending|confirmed|canceled|completed|archived)$")
    format: str = Field(default="excel", pattern="^(excel|csv)$") 