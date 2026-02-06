"""
🛡️ Centralized Configuration Management
Loads and validates all environment variables using Pydantic Settings.
"""

from enum import Enum
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PersonaType(str, Enum):
    """Available persona types for the Actor agent."""
    CONFUSED_SENIOR = "confused_senior"
    EAGER_STUDENT = "eager_student"


class LogFormat(str, Enum):
    """Logging output formats."""
    RICH = "rich"
    JSON = "json"


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ===================================
    # FastAPI Configuration
    # ===================================
    api_key: str = Field(..., description="Secret API key for authentication")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API port")

    # ===================================
    # Redis Configuration
    # ===================================
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    redis_db: int = Field(default=0, ge=0, description="Redis database number")
    redis_password: str = Field(default="", description="Redis password (optional)")
    redis_ttl: int = Field(default=86400, ge=60, description="Session TTL in seconds")

    # ===================================
    # LLM Provider API Keys
    # ===================================
    google_api_key: str = Field(..., description="Google AI API key")
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    openai_api_key: str = Field(default="", description="OpenAI API key (optional backup)")
    groq_api_key: str = Field(default="", description="Groq API key (FREE and FAST!)")

    # ===================================
    # LLM Model Configuration
    # ===================================
    gemini_model: str = Field(
        default="gemini-2.0-flash-exp",
        description="Gemini model for planning tasks"
    )
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model for Actor persona"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model for backup"
    )
    groq_model: str = Field(
        default="llama-3.1-8b-instant",
        description="Groq model (FREE and super fast!)"
    )

    # ===================================
    # GUVI Hackathon Callback
    # ===================================
    guvi_callback_url: str = Field(
        ...,
        description="GUVI callback endpoint URL"
    )
    guvi_api_key: str = Field(..., description="GUVI API key")

    # ===================================
    # Agent Configuration
    # ===================================
    max_conversation_turns: int = Field(
        default=35,  # Increased from 15 to 35 for maximum engagement
        ge=5,
        le=50,
        description="Maximum turns before forcing callback"
    )
    scam_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum scam probability to engage"
    )
    default_persona: PersonaType = Field(
        default=PersonaType.CONFUSED_SENIOR,
        description="Default persona for Actor agent"
    )

    # ===================================
    # Forensics & Security
    # ===================================
    enable_domain_age_check: bool = Field(
        default=True,
        description="Enable WHOIS domain age verification"
    )
    enable_trai_validation: bool = Field(
        default=True,
        description="Enable TRAI header validation"
    )
    enable_safe_browsing: bool = Field(
        default=False,
        description="Enable Google Safe Browsing API (optional)"
    )

    # ===================================
    # Logging
    # ===================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: LogFormat = Field(
        default=LogFormat.RICH,
        description="Logging format"
    )
    enable_national_security_mode: bool = Field(
        default=True,
        description="🛡️ Enable visual excellence in logs"
    )

    # ===================================
    # Environment
    # ===================================
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    debug: bool = Field(default=True, description="Debug mode")

    @field_validator("guvi_callback_url")
    @classmethod
    def validate_callback_url(cls, v: str) -> str:
        """Ensure callback URL is valid HTTPS in production."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Callback URL must start with http:// or https://")
        return v

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION


# Global settings instance
settings = Settings()
