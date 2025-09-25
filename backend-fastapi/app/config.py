"""
Application Configuration using Pydantic Settings
"""
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    PROJECT_NAME: str = "playpark-api"
    API_VERSION: str = "v1"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    PORT: int = Field(default=48080, description="Server port")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    
    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=20, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=14, description="Refresh token expiration in days")
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="Minimum password length")
    
    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Allowed CORS origins (comma-separated)"
    )
    ALLOWED_HOSTS: Optional[List[str]] = Field(default=None, description="Allowed hosts for TrustedHostMiddleware")
    
    # Database
    MONGODB_URI: str = Field(default="mongodb://localhost:27017/playpark", description="MongoDB connection URI")
    MONGODB_MAX_POOL_SIZE: int = Field(default=50, description="MongoDB max pool size")
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = Field(default=2000, description="MongoDB server selection timeout")
    MONGODB_SOCKET_TIMEOUT_MS: int = Field(default=2000, description="MongoDB socket timeout")
    MONGODB_CONNECT_TIMEOUT_MS: int = Field(default=1000, description="MongoDB connect timeout")
    
    # Redis
    REDIS_URI: str = Field(default="redis://localhost:6379/0", description="Redis connection URI")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, description="Redis max connections")
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, description="Redis socket timeout")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW_MINUTES: int = Field(default=15, description="Rate limit window in minutes")
    
    # Idempotency
    IDEMPOTENCY_ENABLED: bool = Field(default=True, description="Enable idempotency")
    IDEMPOTENCY_TTL_SECONDS: int = Field(default=600, description="Idempotency key TTL in seconds")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or console")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_PATH: str = Field(default="/metrics", description="Metrics endpoint path")
    
    # OAuth2
    OAUTH2_CLIENT_ID: str = Field(default="playpark-web", description="OAuth2 client ID")
    OAUTH2_CLIENT_SECRET: str = Field(..., description="OAuth2 client secret")
    OAUTH2_REDIRECT_URI: str = Field(default="http://localhost:3000/callback", description="OAuth2 redirect URI")
    
    # Cookie Settings
    COOKIE_SECURE: bool = Field(default=False, description="Secure cookie flag")
    COOKIE_HTTP_ONLY: bool = Field(default=True, description="HttpOnly cookie flag")
    COOKIE_SAME_SITE: str = Field(default="lax", description="SameSite cookie attribute")
    COOKIE_DOMAIN: Optional[str] = Field(default=None, description="Cookie domain")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if not self.CORS_ORIGINS.strip():
            return ["http://localhost:3000", "http://localhost:8080"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("COOKIE_SAME_SITE")
    def validate_cookie_same_site(cls, v):
        """Validate SameSite cookie attribute"""
        valid_values = ["strict", "lax", "none"]
        if v not in valid_values:
            raise ValueError(f"SameSite must be one of: {valid_values}")
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment value"""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator("LOG_FORMAT")
    def validate_log_format(cls, v):
        """Validate log format"""
        valid_formats = ["json", "console"]
        if v not in valid_formats:
            raise ValueError(f"Log format must be one of: {valid_formats}")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"
    
    @property
    def cookie_settings(self) -> dict:
        """Get cookie settings"""
        return {
            "secure": self.COOKIE_SECURE if self.is_production else False,
            "httponly": self.COOKIE_HTTP_ONLY,
            "samesite": self.COOKIE_SAME_SITE,
            "domain": self.COOKIE_DOMAIN,
        }


# Global settings instance
settings = Settings()
