from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn
from datetime import datetime
import json

from app.core.config import settings
from app.core.rabbitmq import get_rabbitmq_connection
from app.models.notification import Notification, NotificationType
from app.services.notification_service import NotificationService

app = FastAPI(
    title="Notification Service",
    description="A service for sending and managing notifications",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_notification_service():
    return NotificationService()

class NotificationRequest(BaseModel):
    user_id: str
    type: NotificationType
    subject: str
    message: str
    metadata: Optional[Dict] = {}

@app.post("/notifications")
async def send_notification(
    notification: NotificationRequest,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Send a notification to a user.
    """
    try:
        result = await notification_service.send_notification(
            user_id=notification.user_id,
            notification_type=notification.type,
            subject=notification.subject,
            message=notification.message,
            metadata=notification.metadata
        )
        return {"status": "success", "notification_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/notifications")
async def get_user_notifications(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get notifications for a specific user.
    """
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 