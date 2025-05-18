from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict
from datetime import datetime
import uuid

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class Notification(BaseModel):
    id: str = str(uuid.uuid4())
    user_id: str
    type: NotificationType
    subject: str
    message: str
    metadata: Optional[Dict] = {}
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    retry_count: int = 0
    
    class Config:
        from_attributes = True 