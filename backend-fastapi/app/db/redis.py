"""
Redis Configuration and Connection Management
"""
from typing import Optional, Any, Dict
import json
import structlog
import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import settings

logger = structlog.get_logger(__name__)

# Global Redis instance
_redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Get Redis connection instance"""
    global _redis
    
    if _redis is None:
        await connect_to_redis()
    
    return _redis


async def connect_to_redis() -> None:
    """Create Redis connection"""
    global _redis
    
    try:
        logger.info("Connecting to Redis", uri=settings.REDIS_URI)
        
        _redis = redis.from_url(
            settings.REDIS_URI,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            retry_on_timeout=True,
            decode_responses=True,
        )
        
        # Test connection
        await _redis.ping()
        
        logger.info("Successfully connected to Redis")
        
    except Exception as e:
        logger.error("Failed to connect to Redis", error=str(e))
        raise


async def close_redis() -> None:
    """Close Redis connection"""
    global _redis
    
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("Redis connection closed")


async def redis_set(
    key: str, 
    value: Any, 
    expire: Optional[int] = None,
    prefix: str = ""
) -> bool:
    """Set a value in Redis with optional expiration"""
    try:
        redis_client = await get_redis()
        full_key = f"{prefix}:{key}" if prefix else key
        
        # Serialize value if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value)
        
        result = await redis_client.set(full_key, value, ex=expire)
        return bool(result)
        
    except Exception as e:
        logger.error("Error setting Redis key", key=key, error=str(e))
        return False


async def redis_get(key: str, prefix: str = "") -> Optional[Any]:
    """Get a value from Redis"""
    try:
        redis_client = await get_redis()
        full_key = f"{prefix}:{key}" if prefix else key
        
        value = await redis_client.get(full_key)
        
        if value is None:
            return None
        
        # Try to deserialize JSON, fallback to string
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
            
    except Exception as e:
        logger.error("Error getting Redis key", key=key, error=str(e))
        return None


async def redis_delete(key: str, prefix: str = "") -> bool:
    """Delete a key from Redis"""
    try:
        redis_client = await get_redis()
        full_key = f"{prefix}:{key}" if prefix else key
        
        result = await redis_client.delete(full_key)
        return bool(result)
        
    except Exception as e:
        logger.error("Error deleting Redis key", key=key, error=str(e))
        return False


async def redis_exists(key: str, prefix: str = "") -> bool:
    """Check if a key exists in Redis"""
    try:
        redis_client = await get_redis()
        full_key = f"{prefix}:{key}" if prefix else key
        
        result = await redis_client.exists(full_key)
        return bool(result)
        
    except Exception as e:
        logger.error("Error checking Redis key existence", key=key, error=str(e))
        return False


async def redis_increment(key: str, amount: int = 1, prefix: str = "") -> Optional[int]:
    """Increment a numeric value in Redis"""
    try:
        redis_client = await get_redis()
        full_key = f"{prefix}:{key}" if prefix else key
        
        result = await redis_client.incrby(full_key, amount)
        return result
        
    except Exception as e:
        logger.error("Error incrementing Redis key", key=key, error=str(e))
        return None


async def redis_expire(key: str, seconds: int, prefix: str = "") -> bool:
    """Set expiration for a Redis key"""
    try:
        redis_client = await get_redis()
        full_key = f"{prefix}:{key}" if prefix else key
        
        result = await redis_client.expire(full_key, seconds)
        return bool(result)
        
    except Exception as e:
        logger.error("Error setting Redis key expiration", key=key, error=str(e))
        return False


async def redis_get_keys(pattern: str, prefix: str = "") -> list[str]:
    """Get keys matching a pattern"""
    try:
        redis_client = await get_redis()
        search_pattern = f"{prefix}:{pattern}" if prefix else pattern
        
        keys = await redis_client.keys(search_pattern)
        return keys
        
    except Exception as e:
        logger.error("Error getting Redis keys", pattern=pattern, error=str(e))
        return []


# Rate limiting helpers
async def check_rate_limit(
    identifier: str, 
    limit: int, 
    window: int,
    prefix: str = "rate_limit"
) -> Dict[str, Any]:
    """Check if rate limit is exceeded for an identifier"""
    try:
        redis_client = await get_redis()
        key = f"{prefix}:{identifier}"
        
        # Get current count
        current = await redis_client.get(key)
        count = int(current) if current else 0
        
        if count == 0:
            # First request in window
            await redis_client.setex(key, window, 1)
            return {
                "allowed": True,
                "limit": limit,
                "remaining": limit - 1,
                "reset": window
            }
        elif count < limit:
            # Within limit
            await redis_client.incr(key)
            ttl = await redis_client.ttl(key)
            return {
                "allowed": True,
                "limit": limit,
                "remaining": limit - count - 1,
                "reset": ttl
            }
        else:
            # Rate limit exceeded
            ttl = await redis_client.ttl(key)
            return {
                "allowed": False,
                "limit": limit,
                "remaining": 0,
                "reset": ttl
            }
            
    except Exception as e:
        logger.error("Error checking rate limit", identifier=identifier, error=str(e))
        # Fail open - allow request if Redis is down
        return {
            "allowed": True,
            "limit": limit,
            "remaining": limit,
            "reset": window
        }
