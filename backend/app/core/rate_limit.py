from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import time

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings


@dataclass
class RateLimitResult:
    allowed: bool
    count: int


class RateLimiter:
    _memory_store: dict[str, tuple[int, float]] = {}
    _memory_lock = Lock()

    def __init__(self) -> None:
        self._redis: Redis | None = None

    def allow(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        redis_client = self._get_redis()
        if redis_client is not None:
            try:
                count = redis_client.incr(key)
                if count == 1:
                    redis_client.expire(key, window_seconds)
                return RateLimitResult(allowed=count <= limit, count=int(count))
            except RedisError:
                pass
        return self._allow_in_memory(key, limit, window_seconds)

    def _get_redis(self) -> Redis | None:
        if self._redis is None:
            try:
                self._redis = Redis.from_url(settings.redis_url, decode_responses=True)
            except RedisError:
                return None
        return self._redis

    def _allow_in_memory(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        now = time()
        with self._memory_lock:
            current = self._memory_store.get(key)
            if current is None or current[1] <= now:
                count = 1
                self._memory_store[key] = (count, now + window_seconds)
            else:
                count = current[0] + 1
                self._memory_store[key] = (count, current[1])
        return RateLimitResult(allowed=count <= limit, count=count)


rate_limiter = RateLimiter()
