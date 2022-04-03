import shutil
from typing import BinaryIO
from urllib.parse import urlparse

from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.sftp_file import SFTPFile

from provider.base import BaseDownloadInterface

CONNECTION_TIMEOUT = 5
WAIT_FOR_RECONNECT = 30


class sFTPDownloadInterface(BaseDownloadInterface):

    def get_filepath(self, location) -> str:
        parsed_url = urlparse(location)
        return f'{parsed_url.hostname}/{parsed_url.path}'

    def download(self, file: BinaryIO, location: str) -> None:
        params = urlparse(location)
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(
            hostname=params.hostname,
            port=params.port or 22,
            timeout=CONNECTION_TIMEOUT,
            username=params.username,
            password=params.password
        )
        sftp = client.open_sftp()

        dst_file: SFTPFile = sftp.open(params.path, 'r')
        shutil.copyfileobj(dst_file, file)

        sftp.close()
        client.close()
