"""
Redis cache manager for Synapse.
Handles caching of thread summaries and other frequently accessed data.
"""
import json
from typing import Dict, Optional
import redis.asyncio as redis
from datetime import timedelta
from ..config import get_settings

class RedisCache:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None
    ):
        """Initialize Redis cache.
        
        Args:
            host: Redis host (optional, uses config if None)
            port: Redis port (optional, uses config if None)
            db: Redis database number (optional, uses config if None)
            password: Redis password (optional, uses config if None)
        """
        settings = get_settings()
        self.redis = redis.Redis(
            host=host or settings.redis_host,
            port=port or settings.redis_port,
            db=db or settings.redis_db,
            password=password or settings.redis_password,
            decode_responses=True
        )
        
    async def get_thread_summary(self, channel: str, thread_ts: str) -> Optional[Dict]:
        """Get cached thread summary.
        
        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp
            
        Returns:
            Cached summary dictionary or None if not found
        """
        key = f"thread_summary:{channel}:{thread_ts}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
        
    async def set_thread_summary(
        self,
        channel: str,
        thread_ts: str,
        summary: Dict,
        ttl: Optional[int] = None
    ):
        """Cache thread summary.
        
        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp
            summary: Summary dictionary to cache
            ttl: Time to live in seconds (optional, uses config if None)
        """
        settings = get_settings()
        key = f"thread_summary:{channel}:{thread_ts}"
        await self.redis.setex(
            key,
            timedelta(seconds=ttl or settings.cache_ttl),
            json.dumps(summary)
        )
        
    async def invalidate_thread_summary(self, channel: str, thread_ts: str):
        """Remove cached thread summary.
        
        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp
        """
        key = f"thread_summary:{channel}:{thread_ts}"
        await self.redis.delete(key) 