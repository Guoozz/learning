import redis
import functools

client = redis.StrictRedis(host="localhost", port=6379)


def cache(ex=10):

    def decorator(func):

        @functools.wraps(func)
        def _wrap(*args, **kwargs):
            key = func.__name__
            value = client.get(key)
            if value:
                print("value from cache: {}".format(value))
                return value
            else:
                value = func(*args, **kwargs)
                print("value from computing: {}".format(value))
                import time
                time.sleep(1)
                client.set(key, value, ex=ex)
                return value

        return _wrap

    return decorator


@cache(ex=100)
def compute():
    import time
    time.sleep(100)
    return 3


while True:
    compute()
