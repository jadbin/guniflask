import gzip
from typing import List, Union

from pydantic import BaseModel

from guniflask.web.request_filter import RequestFilter


class GzipOption(BaseModel):
    compress_level: int = 6
    compress_types: Union[List[str], None] = None
    compress_min_length: int = 1024


DEFAULT_COMPRESS_TYPES = [
    'application/json',
    'text/css',
    'text/html',
    'text/javascript',
    'text/xml',
]


class GzipFilter(RequestFilter):

    def __init__(self, **kwargs):
        self.option = GzipOption(**kwargs)
        if not self.option.compress_types:
            self.option.compress_types = DEFAULT_COMPRESS_TYPES

    def after_request(self, response):
        return self._gzip_compress(response)

    def _gzip_compress(self, response):
        if response.mimetype not in self.option.compress_types \
                or response.content_length < self.option.compress_min_length \
                or "Content-Encoding" in response.headers:
            return response

        response.set_data(
            gzip.compress(
                response.get_data(),
                compresslevel=self.option.compress_level,
            )
        )
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = response.content_length
        return response
