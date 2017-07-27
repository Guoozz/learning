from celery import Celery
import time

app = Celery('test', broker="redis://127.0.0.1:6379", backend="redis://127.0.0.1:6379")

app.conf.worker_prefetch_multiplier = 4
app.conf.task_routes = {
    "test.*": {
        'queue': 'test'
    }
}


@app.task(track_started=True)
def fast(x, y):
    time.sleep(1)
    return x + y


@app.task(track_started=True)
def slow(x, y):
    time.sleep(60)
    return x + y
