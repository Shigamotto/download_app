from typing import BinaryIO
from urllib.parse import urlparse

import requests

from .base import BaseDownloadInterface

DEFAULT_CHUNK_SIZE = 8192


class HTTPDownloadInterface(BaseDownloadInterface):

    _verify = False

    def get_filepath(self, location) -> str:
        parsed_url = urlparse(location)
        return f'{parsed_url.hostname}/{parsed_url.path}'

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
