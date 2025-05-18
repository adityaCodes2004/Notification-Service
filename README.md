# Notification Service

A robust notification service that supports multiple notification channels (Email, SMS, and in-app) with message queuing and retry mechanisms.

## Features

- Multiple notification channels (Email, SMS, in-app)
- Message queuing using RabbitMQ
- Retry mechanism for failed notifications
- RESTful API endpoints
- Scalable architecture

## Prerequisites

- Python 3.8+
- RabbitMQ server
- SMTP server (for email notifications)
- SMS provider credentials (for SMS notifications)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd notification-service
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMS_PROVIDER_API_KEY=your-sms-provider-api-key
```

5. Start RabbitMQ server:
```bash
# Using Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Send Notification
- **POST** `/notifications`
- Request body:
```json
{
    "user_id": "string",
    "type": "email|sms|in_app",
    "subject": "string",
    "message": "string",
    "metadata": {}
}
```

### Get User Notifications
- **GET** `/users/{id}/notifications`
- Query parameters:
  - `limit`: int (default: 10)
  - `offset`: int (default: 0)

## Architecture

The service uses a message queue (RabbitMQ) to handle notifications asynchronously. When a notification request is received:

1. The request is validated and stored in the database
2. A message is published to RabbitMQ
3. Notification workers process the message and attempt to send the notification
4. Failed notifications are retried with exponential backoff

## Assumptions

1. Email notifications use SMTP
2. SMS notifications require a third-party provider
3. In-app notifications are stored in a database and retrieved via API
4. Notifications are processed asynchronously
5. Failed notifications are retried up to 3 times with exponential backoff
6. The service maintains a record of all notifications in a database

## Error Handling

- Failed notifications are logged and retried
- Maximum retry attempts: 3
- Retry delay: Exponential backoff (1s, 2s, 4s)
- Failed notifications after all retries are marked as failed in the database

## Security

- API endpoints are protected with authentication
- Sensitive credentials are stored in environment variables
- All API requests are validated using Pydantic models

## API Documentation

Once the app is running, access the interactive API docs at:
[http://localhost:8000/docs](http://localhost:8000/docs)

## Deployed Application (Optional)

If deployed, you can try the live API here:
[https://your-app-name.onrender.com/docs](https://your-app-name.onrender.com/docs)

*(Replace the above link with your actual deployed URL after deployment.)* 