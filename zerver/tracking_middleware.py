import json
import logging

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from django.http import HttpRequest, StreamingHttpResponse
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

logger = logging.getLogger(__name__)

class TrackUsers(MiddlewareMixin):
    def process_response(self, request: HttpRequest,
                         response: StreamingHttpResponse) -> StreamingHttpResponse:

        if request.path == '/json/users/me/presence' and settings.POST_URL:
            loop = IOLoop.current()
            loop.spawn_callback(async_fetch_gen, settings.POST_URL, response.content)
            try:
                loop.start()
            except RuntimeError:
                pass  # In case the loop is already started

        return response


@gen.coroutine
def async_fetch_gen(url, data):
    http_client = AsyncHTTPClient()

    headers = {'Content-Type': 'application/json'}
    response = yield http_client.fetch(url,
                                       raise_error=False,
                                       method='POST',
                                       body=data,
                                       headers=headers)

    body = response.body
    if response.code == 200:
        logger.info(json.loads(body.decode('utf8')))
    else:
        logger.warn("{code} - {reason}".format(code=response.code, reason=response.reason))

    raise gen.Return(body)
