import os
import shutil
from typing import BinaryIO
from urllib.parse import urlparse

from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.sftp_file import SFTPFile

from provider.base import BaseDownloadInterface

CONNECTION_TIMEOUT = 5
WAIT_FOR_RECONNECT = 30


class sFTPDownloadInterface(BaseDownloadInterface):

    def get_filename(self, location) -> str:
        parsed_url = urlparse(location)
        local_filename = parsed_url.path.split('/')[-1]
        return str(local_filename)

    def is_same_file(self, location: str, exists_file_stat: os.stat_result):
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

        stat = sftp.stat(params.path)
        if (
            stat.st_size == exists_file_stat.st_size
            and stat.st_mtime < exists_file_stat.st_mtime
        ):
            return True

        return False

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
