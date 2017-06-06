from tornado import gen
from tornado.httpclient import AsyncHTTPClient


async def fetch_coroutine(url):
    http_client = AsyncHTTPClient()
    response = await http_client.fetch(url)
    return response.body


if __name__ == "__main__":
    body = fetch_coroutine("http://www.baidu.com")

