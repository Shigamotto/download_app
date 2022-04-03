import datetime
import os
from ftplib import FTP
from typing import BinaryIO
from urllib.parse import urlparse

from dateutil import parser

from provider.base import BaseDownloadInterface

CONNECTION_TIMEOUT = 5
WAIT_FOR_RECONNECT = 30


class FTPDownloadInterface(BaseDownloadInterface):

    sleep_on_retry = True
    sleep_timeout = 30

    def get_filename(self, location) -> str:
        parsed_url = urlparse(location)
        local_filename = parsed_url.path.split('/')[-1]
        return str(local_filename)

    def is_same_file(self, location: str, exists_file_stat: os.stat_result) -> bool:
        ftp_params = urlparse(location)
        client = FTP()
        client.connect(host=ftp_params.hostname, port=ftp_params.port or 21, timeout=CONNECTION_TIMEOUT)
        client.login(user=ftp_params.username, passwd=ftp_params.password)
        client.voidcmd('TYPE I')

        opinion = False
        dst_filesize = client.size(ftp_params.path)
        if dst_filesize == exists_file_stat.st_size:
            dst_file_modifications_time_string = client.voidcmd(f'MDTM {ftp_params.path}')[4:].strip()
            dst_file_modifications_time = parser.parse(dst_file_modifications_time_string)
            if dst_file_modifications_time < datetime.datetime.fromtimestamp(exists_file_stat.st_mtime):
                opinion = True

        client.close()
        return opinion

    def download(self, file: BinaryIO, location: str) -> None:
        ftp_params = urlparse(location)
        client = FTP()
        client.connect(host=ftp_params.hostname, port=ftp_params.port or 21, timeout=CONNECTION_TIMEOUT)
        client.login(user=ftp_params.username, passwd=ftp_params.password)
        client.voidcmd('TYPE I')
        client.retrbinary('RETR %s' % ftp_params.path, file.write, rest=file.tell())
