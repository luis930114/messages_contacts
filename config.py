import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contacts.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Email configuration
SMTP_CONFIG = {
    "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "user": os.getenv("EMAIL_USER", "test@example.com"),
    "password": os.getenv("EMAIL_PASSWORD", "password")
}

# External services
SUPPORT_SERVICE_URL = os.getenv("SUPPORT_SERVICE_URL", "http://localhost:8001/support-service")

# API configuration
API_CONFIG = {
    "host": os.getenv("API_HOST", "0.0.0.0"),
    "port": int(os.getenv("API_PORT", "8000")),
    "debug": os.getenv("DEBUG", "True").lower() == "true"
}