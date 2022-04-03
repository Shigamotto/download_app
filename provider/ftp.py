from ftplib import FTP
from typing import BinaryIO
from urllib.parse import urlparse

from provider.base import BaseDownloadInterface

CONNECTION_TIMEOUT = 5
WAIT_FOR_RECONNECT = 30


class FTPDownloadInterface(BaseDownloadInterface):

    sleep_on_retry = True
    sleep_timeout = 30

    def get_filepath(self, location) -> str:
        parsed_url = urlparse(location)
        return f'{parsed_url.hostname}{parsed_url.path}'

    def download(self, file: BinaryIO, location: str) -> None:
        ftp_params = urlparse(location)
        client = FTP()
        client.connect(host=ftp_params.hostname, port=ftp_params.port or 21, timeout=CONNECTION_TIMEOUT)
        client.login(user=ftp_params.username, passwd=ftp_params.password)
        client.voidcmd('TYPE I')
        client.retrbinary('RETR %s' % ftp_params.path, file.write, rest=file.tell())
