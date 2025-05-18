from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # RabbitMQ settings
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # SMTP settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Twilio settings
    TWILIO_ACCOUNT_SID: str = ""
    SMS_PROVIDER_API_KEY: str = ""  # This will be your Twilio Auth Token
    TWILIO_PHONE_NUMBER: str = ""
    
    # Application settings
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 1  # in seconds
    
    class Config:
        env_file = ".env"

settings = Settings() 