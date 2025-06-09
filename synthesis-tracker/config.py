"""
Configuration for Synthesis Tracker MCP server.
"""

import os
from typing import Optional
from pydantic import BaseSettings, EmailStr


class SynthesisConfig(BaseSettings):
    """Configuration settings for Synthesis tracker."""
    
    # Email settings for login code monitoring
    email_server: str = os.getenv("EMAIL_SERVER", "imap.gmail.com")
    email_port: int = int(os.getenv("EMAIL_PORT", "993"))
    email_username: str = os.getenv("EMAIL_USERNAME", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")
    email_use_ssl: bool = os.getenv("EMAIL_USE_SSL", "true").lower() == "true"
    
    # Synthesis.com settings
    synthesis_email: EmailStr = os.getenv("SYNTHESIS_EMAIL", "")
    synthesis_url: str = os.getenv("SYNTHESIS_URL", "https://synthesis.com")
    
    # Database settings
    database_path: str = os.getenv("DATABASE_PATH", "./synthesis_data.db")
    
    # Notification settings
    notification_enabled: bool = os.getenv("NOTIFICATION_ENABLED", "true").lower() == "true"
    notification_times: str = os.getenv("NOTIFICATION_TIMES", "09:00,15:00,19:00")
    
    # Browser automation settings
    headless_browser: bool = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"
    browser_timeout: int = int(os.getenv("BROWSER_TIMEOUT", "30"))
    
    # Study tracking settings
    minimum_study_minutes: int = int(os.getenv("MINIMUM_STUDY_MINUTES", "15"))
    study_goal_minutes: int = int(os.getenv("STUDY_GOAL_MINUTES", "30"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global config instance
config = SynthesisConfig()