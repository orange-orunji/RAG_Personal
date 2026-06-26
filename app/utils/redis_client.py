import redis
from app.config.settings import settings as st

_redis_client = None

def get_redis():
    """懒加载 Redis 连接，连接失败返回 None 而不是崩溃"""
    global _redis_client
    if _redis_client is None:
        try:
            s = st()
            _redis_client = redis.Redis(
                host=s.REDIS_HOST,
                port=s.REDIS_PORT,
                db=s.REDIS_DB,
                decode_responses=True
            )
            _redis_client.ping()
            print(f"Redis 连接成功: host={s.REDIS_HOST}, port={s.REDIS_PORT}, db={s.REDIS_DB}")
        except redis.ConnectionError:
            print("⚠️ Redis 未连接，缓存功能将不可用")
            _redis_client = None
    return _redis_client

redis_client_connect = get_redis()
