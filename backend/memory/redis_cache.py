"""
Redis cache manager for Synapse.
Handles caching of thread summaries and other frequently accessed data.
"""
import json
from typing import Dict, Optional
import redis.asyncio as redis
from datetime import timedelta

class RedisCache:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None
    ):
        """Initialize Redis cache.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
        """
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
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
        ttl: int = 3600  # 1 hour default TTL
    ):
        """Cache thread summary.
        
        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp
            summary: Summary dictionary to cache
            ttl: Time to live in seconds
        """
        key = f"thread_summary:{channel}:{thread_ts}"
        await self.redis.setex(
            key,
            timedelta(seconds=ttl),
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