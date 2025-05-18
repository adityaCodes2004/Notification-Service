import json
import asyncio
from app.core.rabbitmq import consume_messages
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType

async def process_notification(ch, method, properties, body):
    """Process a notification from the queue."""
    try:
        data = json.loads(body)
        notification_service = NotificationService()
        
        # Get the notification from storage
        notification = notification_service.notifications.get(data['notification_id'])
        if not notification:
            print(f"Notification {data['notification_id']} not found")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Process based on notification type
        if notification.type == NotificationType.EMAIL:
            await notification_service.send_email(notification)
        elif notification.type == NotificationType.SMS:
            await notification_service.send_sms(notification)
        elif notification.type == NotificationType.IN_APP:
            await notification_service.send_in_app(notification)
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Error processing notification: {str(e)}")
        # Reject the message and requeue if retry count is less than max
        if notification and notification.retry_count < 3:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Start the notification worker."""
    channel, connection = consume_messages()
    
    # Set up consumer
    channel.basic_consume(
        queue='notifications',
        on_message_callback=lambda ch, method, properties, body: asyncio.run(
            process_notification(ch, method, properties, body)
        )
    )
    
    print('Started consuming notifications...')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == '__main__':
    main() 