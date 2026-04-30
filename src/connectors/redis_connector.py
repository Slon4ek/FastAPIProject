import logging

import redis.asyncio as redis
from typing import Any

logger = logging.getLogger(__name__)


class RedisManager:
    redis_client: redis.Redis

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def connect(self):
        logger.info(f"Connecting to Redis server on {self.host}:{self.port}")
        self.redis_client = await redis.Redis(host=self.host, port=self.port, decode_responses=True)
        logger.info(f"Connected to Redis server on {self.host}:{self.port}")

    async def set(self, key: str, value: Any, expire: int | None = None):
        if expire:
            await self.redis_client.set(key, value, ex=expire)
        else:
            await self.redis_client.set(key, value)

    async def get(self, key: str) -> Any:
        return await self.redis_client.get(key)

    async def delete(self, key: str):
        await self.redis_client.delete(key)

    async def close(self):
        if self.redis_client is not None:
            await self.redis_client.close()
