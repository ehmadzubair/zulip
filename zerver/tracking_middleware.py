import json

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from django.http import HttpRequest, StreamingHttpResponse
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop


class TrackUsers(MiddlewareMixin):
    def process_response(self, request: HttpRequest,
                         response: StreamingHttpResponse) -> StreamingHttpResponse:

        if request.path == '/json/users/me/presence' and settings.POST_URL:
            loop = IOLoop.current()
            loop.spawn_callback(async_fetch_gen, settings.POST_URL, str(response.content))
            try:
                loop.start()
            except RuntimeError:
                pass  # In case the loop is already started

        return response


@gen.coroutine
def async_fetch_gen(url, data):
    http_client = AsyncHTTPClient()

    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data)
    response = yield http_client.fetch(url,
                                       raise_error=False,
                                       method='POST',
                                       body=json_data,
                                       headers=headers)

    # Add logging
    raise gen.Return(response.body)
