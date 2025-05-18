import pika
from app.core.config import settings
import json
from typing import Any, Dict

def get_rabbitmq_connection():
    """Get a connection to RabbitMQ."""
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def publish_message(message: Dict[str, Any], queue_name: str = "notifications"):
    """Publish a message to RabbitMQ."""
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Declare the queue
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Publish the message
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    
    connection.close()

def consume_messages(queue_name: str = "notifications"):
    """Consume messages from RabbitMQ."""
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Declare the queue
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Set prefetch count
    channel.basic_qos(prefetch_count=1)
    
    return channel, connection 