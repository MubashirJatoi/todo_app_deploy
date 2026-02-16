import os
from typing import Optional
from pydantic_settings import Settings


class Config(Settings):
    # Cohere API configuration
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")

    # Phase 2 API endpoints
    PHASE2_API_BASE_URL: str = os.getenv("PHASE2_API_BASE_URL", "https://mubashirjatoi-todo-ai-chatbot.hf.space")
    PHASE2_API_TIMEOUT: int = int(os.getenv("PHASE2_API_TIMEOUT", "30"))

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

    # JWT configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-here-make-it-long-and-random")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Application settings
    APP_NAME: str = "AI Chatbot Service"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


config = Config()