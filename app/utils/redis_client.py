import redis

from app.config.settings import settings as  st
s = st()
print(f"Redis 连接: host={s.REDIS_HOST}, port={s.REDIS_PORT}, db={s.REDIS_DB}")
redis_client_connect = redis.Redis(host=s.REDIS_HOST,
                                   port=s.REDIS_PORT,
                                   db=s.REDIS_DB,
                                   decode_responses=True)
