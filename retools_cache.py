from retools.cache import CacheRegion, cache_region

CacheRegion.add_region("test", expires=100, redis_expiration=60 * 60 * 24)


@cache_region("test")
def some_fun(a):
    return a

while True:
    print(some_fun("second2"))
