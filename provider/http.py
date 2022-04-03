import os
import urllib
from typing import BinaryIO
from urllib.parse import urlparse

import requests

from .base import BaseDownloadInterface

DEFAULT_CHUNK_SIZE = 8192


class HTTPDownloadInterface(BaseDownloadInterface):

    _verify = False

    def get_filename(self, location) -> str:
        parsed_url = urlparse(location)
        local_filename = parsed_url.path.split('/')[-1]
        return str(local_filename)

    def is_same_file(self, location: str, exists_file_stat: os.stat_result) -> bool:
        key_word = 'Content-Length'

        head = requests.head(location, verify=self._verify)
        content_length = head.headers.get(key_word)
        if not content_length:
            get = requests.get(location, stream=True, verify=self._verify)
            content_length = get.headers.get(key_word)
        if not content_length:
            req = urllib.request.Request(location, method='HEAD')
            f = urllib.request.urlopen(req)
            content_length = f.headers.get(key_word)

        return content_length == exists_file_stat.st_size

    def download(self, file: BinaryIO, location: str) -> None:
        resume_download_header = {'Range': 'bytes=%d-' % file.tell()}
        with requests.get(location, headers=resume_download_header, stream=True, verify=self._verify) as r:
            r.raise_for_status()
            for chunk in r.iter_content(
                    chunk_size=DEFAULT_CHUNK_SIZE
            ):
                file.write(chunk)


class HTTPsDownloadInterface(HTTPDownloadInterface):
    _verify = True
