## 抽象
获取集群的状态方式，有2种方式
- prometheus
- redis
路由条件:
- prometheus: redis没有相对应的`key`
- redis: 用户执行某个操作,触发redis `set`操作

```python
    def some_fun():
        if is_key_exists(key):
            value = redis_get(key)
            return value
        else:
            while True:
                value = get_lastest_value()
                redis_set(key, value)
                time.sleep(10)
```
