import logging

import redis.asyncio as aioredis
from typing import Any

logger = logging.getLogger(__name__)


class RedisManager:
    client: aioredis.Redis

    def __init__(self, host: str, port: int, password: str) -> None:
        self.host = host
        self.port = port
        self.password = password

    async def connect(self) -> bool:
        try:
            self.client = aioredis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=10,
            )
            # Проверка подключения
            await self.client.ping()
            logger.info(f"Успешное подключение к Redis {self.host}:{self.port}")
            return True
        except aioredis.AuthenticationError as e:
            logger.error(f"Ошибка аутентификации Redis: {e}")
            return False
        except aioredis.ConnectionError as e:
            logger.error(f"Ошибка подключения к Redis: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при подключении к Redis: {e}")
            return False

    async def set(self, key: str, value: Any, expire: int | None = None):
        if expire:
            await self.client.set(key, value, ex=expire)
        else:
            await self.client.set(key, value)

    async def get(self, key: str) -> Any:
        return await self.client.get(key)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def close(self):
        if self.client is not None:
            await self.client.close()
