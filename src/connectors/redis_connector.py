import redis.asyncio as redis
from typing import Any, Optional


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        if self.redis_client is None:
            self.redis_client = await redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=True
            )

    async def set(self, key: str, value: Any, expire: Optional[int] = None):
        if self.redis_client is None:
            await self.connect()

        if expire:
            await self.redis_client.setex(key, expire, value)
        else:
            await self.redis_client.set(key, value)

    async def get(self, key: str) -> Any:
        if self.redis_client is None:
            await self.connect()

        return await self.redis_client.get(key)

    async def delete(self, key: str):
        if self.redis_client is None:
            await self.connect()

        await self.redis_client.delete(key)

    async def close(self):
        if self.redis_client is not None:
            await self.redis_client.close()
