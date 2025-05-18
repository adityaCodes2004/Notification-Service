from typing import List, Optional
from datetime import datetime
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tenacity import retry, stop_after_attempt, wait_exponential
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.core.config import settings
from app.core.rabbitmq import publish_message
from app.models.notification import Notification, NotificationType, NotificationStatus

class NotificationService:
    def __init__(self):
        self.notifications = {}  # In-memory storage for demo purposes
        # Initialize Twilio client
        self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.SMS_PROVIDER_API_KEY)
        
    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        subject: str,
        message: str,
        metadata: Optional[dict] = None
    ) -> Notification:
        """Create and queue a notification."""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            subject=subject,
            message=message,
            metadata=metadata or {}
        )
        
        # Store notification
        self.notifications[notification.id] = notification
        
        # Queue notification for processing
        publish_message({
            "notification_id": notification.id,
            "type": notification_type,
            "user_id": user_id,
            "subject": subject,
            "message": message,
            "metadata": metadata
        })
        
        return notification
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user."""
        user_notifications = [
            n for n in self.notifications.values()
            if n.user_id == user_id
        ]
        return sorted(
            user_notifications,
            key=lambda x: x.created_at,
            reverse=True
        )[offset:offset + limit]
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=settings.RETRY_DELAY)
    )
    async def send_email(self, notification: Notification) -> bool:
        """Send an email notification."""
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USER
            msg['To'] = notification.metadata.get('email')
            msg['Subject'] = notification.subject
            
            msg.attach(MIMEText(notification.message, 'plain'))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            notification.status = NotificationStatus.SENT
            notification.updated_at = datetime.utcnow()
            return True
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.retry_count += 1
            notification.updated_at = datetime.utcnow()
            raise e
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=settings.RETRY_DELAY)
    )
    async def send_sms(self, notification: Notification) -> bool:
        """Send an SMS notification using Twilio."""
        try:
            # Send SMS using Twilio
            message = self.twilio_client.messages.create(
                body=notification.message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=notification.metadata.get('phone')
            )
            
            # Check if message was sent successfully
            if message.status in ['queued', 'sent', 'delivered']:
                notification.status = NotificationStatus.SENT
                notification.updated_at = datetime.utcnow()
                return True
            else:
                raise Exception(f"SMS sending failed: {message.status}")
                
        except TwilioRestException as e:
            notification.status = NotificationStatus.FAILED
            notification.retry_count += 1
            notification.updated_at = datetime.utcnow()
            raise Exception(f"Twilio error: {str(e)}")
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.retry_count += 1
            notification.updated_at = datetime.utcnow()
            raise e
    
    async def send_in_app(self, notification: Notification) -> bool:
        """Send an in-app notification."""
        try:
            # For in-app notifications, we just store them in our system
            notification.status = NotificationStatus.SENT
            notification.updated_at = datetime.utcnow()
            return True
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.retry_count += 1
            notification.updated_at = datetime.utcnow()
            raise e 