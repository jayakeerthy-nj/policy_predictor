from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings


def get_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def redis_health() -> str:
    try:
        client = get_redis_client()
        client.ping()
        return "ok"
    except RedisError:
        return "degraded"

