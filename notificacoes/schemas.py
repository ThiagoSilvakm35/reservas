from ninja import Schema
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class NotificationOutSchema(Schema):
    id: int
    notification_type: str
    title: str
    message: str
    status: str
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class NotificationFilterSchema(Schema):
    status: Optional[str] = Field(default=None, pattern="^(pending|sent|failed|read)$")
    notification_type: Optional[str] = Field(default=None, pattern="^(confirmation|reminder|review|report|cancellation|waiting_list)$")
    page: int = 1
    page_size: int = Field(default=10, le=100)

class NotificationMarkAsReadSchema(Schema):
    notification_ids: List[int]

class EmailTemplateCreateSchema(Schema):
    name: str
    notification_type: str = Field(pattern="^(confirmation|reminder|review|report|cancellation|waiting_list)$")
    subject: str
    body_text: str
    body_html: str
    language: str = Field(pattern="^(pt-br|en|es)$")
    is_active: bool = True

class EmailTemplateUpdateSchema(Schema):
    name: Optional[str] = None
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    is_active: Optional[bool] = None

class EmailTemplateOutSchema(Schema):
    id: int
    name: str
    notification_type: str
    subject: str
    body_text: str
    body_html: str
    language: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class EmailTemplateFilterSchema(Schema):
    notification_type: Optional[str] = Field(default=None, pattern="^(confirmation|reminder|review|report|cancellation|waiting_list)$")
    language: Optional[str] = Field(default=None, pattern="^(pt-br|en|es)$")
    is_active: Optional[bool] = None 