"""
Application Configuration using Pydantic Settings
"""
from typing import List, Optional, Dict
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
        default="http://localhost:3000,http://localhost:8080,http://localhost:3001,http://localhost:3002",
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
    
    # Media Storage (S3/MinIO)
    S3_ENDPOINT: str = Field(default="http://localhost:9000", description="S3-compatible storage endpoint")
    S3_REGION: str = Field(default="us-east-1", description="S3 region")
    S3_BUCKET: str = Field(default="media", description="S3 bucket for media storage")
    S3_ACCESS_KEY: str = Field(default="minioadmin", description="S3 access key")
    S3_SECRET_KEY: str = Field(default="minioadmin", description="S3 secret key")
    S3_USE_SSL: bool = Field(default=False, description="Use SSL for S3 connections")
    S3_SIGNED_URL_TTL: int = Field(default=3600, description="Signed URL TTL in seconds")
    S3_MAX_FILE_SIZE: int = Field(default=10485760, description="Maximum file size in bytes (10MB)")
    S3_ALLOWED_MIME_TYPES: str = Field(
        default="image/jpeg,image/png,image/webp,image/avif,image/gif",
        description="Allowed MIME types (comma-separated)"
    )
    
    # Media Processing
    MEDIA_CDN_BASE_URL: Optional[str] = Field(default=None, description="CDN base URL for media delivery")
    MEDIA_PROCESSING_ENABLED: bool = Field(default=True, description="Enable image processing for variants")
    MEDIA_VARIANT_SIZES: str = Field(
        default="thumb:150x150,sm:300x300,md:600x600,lg:1200x1200",
        description="Image variant sizes (format: name:WxH,name:WxH)"
    )
    MEDIA_STRIP_EXIF: bool = Field(default=True, description="Strip EXIF data from images")
    MEDIA_COMPRESS_QUALITY: int = Field(default=85, description="Image compression quality (1-100)")
    MEDIA_DOMINANT_COLOR: bool = Field(default=True, description="Extract dominant color from images")
    
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
    
    @property
    def allowed_mime_types_list(self) -> List[str]:
        """Get allowed MIME types as a list"""
        return [mime.strip() for mime in self.S3_ALLOWED_MIME_TYPES.split(",") if mime.strip()]
    
    @property
    def media_variant_sizes_dict(self) -> Dict[str, Dict[str, int]]:
        """Get media variant sizes as a dictionary"""
        variants = {}
        for variant in self.MEDIA_VARIANT_SIZES.split(","):
            if ":" in variant:
                name, size = variant.split(":", 1)
                if "x" in size:
                    width, height = size.split("x", 1)
                    variants[name.strip()] = {
                        "width": int(width.strip()),
                        "height": int(height.strip())
                    }
        return variants
    
    @property
    def media_base_url(self) -> str:
        """Get media base URL (CDN or S3 endpoint)"""
        if self.MEDIA_CDN_BASE_URL:
            return self.MEDIA_CDN_BASE_URL.rstrip("/")
        return self.S3_ENDPOINT.rstrip("/")


# Global settings instance
settings = Settings()
