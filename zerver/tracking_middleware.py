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
            loop.spawn_callback(post_tracking_data, settings.POST_URL, response.content)
            try:
                loop.start()
            except RuntimeError:
                pass  # In case the loop is already started

        return response


@gen.coroutine
def post_tracking_data(url, data):
    """
    Async coroutine to post (tracking) data to the url.

    :param url: The url to post the data to
    :param data: Tracking data

    {
      "server_timestamp": 1553856532.6151256561,
      "msg": "",
      "presences": {
        "ZOE@zulip.com": {
          "website": {
            "status": "active",
            "pushable": false,
            "timestamp": 1553168895,
            "client": "website"
          },
          "aggregated": {
            "status": "active",
            "timestamp": 1553168895,
            "client": "website"
          }
        },
        "hamlet@zulip.com": {
          ...
        },
        ...
      },
      "result": "success"
    }

    :return: Response body from the remote url
    """
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
