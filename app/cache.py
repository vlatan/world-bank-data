import json
import functools
import contextvars
from typing import Callable, Hashable, Any
from redis.exceptions import ConnectionError
from datetime import datetime, timedelta, timezone


redis_client_ctx = contextvars.ContextVar("redis_client")


def cache_data(_func: Callable | None = None, *, ttl: int = 86400) -> Callable:
    """
    Cache data in Redis.
    If Redis not available cache in functools.lru_cache.
    If TTL not specified, default is 1 day, 86400 seconds.
    """

    def decorator(func: Callable) -> Callable:

        func.cache_callable = functools.lru_cache(maxsize=128)(func)
        func.lifetime = timedelta(seconds=ttl)
        func.expiretime = datetime.now(timezone.utc) + func.lifetime

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # get redis client object from context variable
                redis_client = redis_client_ctx.get()

                # construct redis key
                hash_args = [str(arg) for arg in args if isinstance(arg, Hashable)]
                key = "_".join([func.__name__] + hash_args)

                # try to return from redis
                result = redis_client.get(key)
                if isinstance(result, (str, bytes, bytearray)):
                    return json.loads(result)

                # get uncached result
                result = func(*args, **kwargs)

                # cache to redis
                redis_client.set(name=key, value=json.dumps(result), ex=ttl)

                return result

            except ConnectionError:
                if now := datetime.now(timezone.utc) >= func.expiretime:
                    func.cache_callable.cache_clear()
                    func.expiretime = now + func.lifetime

                return func.cache_callable(*args, **kwargs)

        return wrapper

    if _func is not None:
        return decorator(_func)

    return decorator
