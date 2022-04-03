import asyncio
import logging
import os
import time
from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor
from typing import List

from provider.base import BaseDownloadInterface
from provider.exceptions import InterfaceNotFound

logger = logging.getLogger(__name__)

MAX_WORKERS = 10


class Service:
    registered = {}

    def register_interface(self, condition, interface: BaseDownloadInterface.__class__):
        """
            The method of registering the download interface in the service

            :param condition: under this condition the interface will be called
            :param interface: class inheritance from BaseDownloadInterface, not object

            :return:
        """
        self.registered[condition] = interface

    def get_interface(self, location) -> BaseDownloadInterface.__class__:
        """
            Method of getting class of BaseDownloadInterface from requested location string
            Method checks the location string for compliance with the registered
            conditions and returns if it passes

            :param location: the requested string from which the download request should be made

            :return: class inheritance from BaseDownloadInterface: class for create object of interface class
        """
        for condition, interface_class in self.registered.items():
            if condition(location):
                return interface_class
        raise InterfaceNotFound

    @classmethod
    def _download(cls, interface: BaseDownloadInterface, location: str, max_retries: int) -> None:
        """
            The method wraps the interface.download method into a package of basic checks,
            and also provides the required number of attempts

            The file in the form of a context manager is passed on to the interface,
            it is recommended to use the value file.tell() for continue download after disconnect

            :param interface: object of calling class of inheritance BaseDownloadInterface
            :param location: the requested string from which the download request should be made
            :param max_retries: number of max retries

            :return:
        """
        _tries = 0
        *filepath, filename = f'storage/{interface.get_filepath(location)}'.split('/')
        path = os.path.join(*filepath)
        os.makedirs(path)

        with open(f'{path}/{filename}', 'wb') as file:
            while _tries <= max_retries:
                try:
                    downloaded = interface.download(file, location)
                    return downloaded
                except interface.retry_on as e:
                    logger.error('Start retry with %s', e)
                    if interface.sleep_on_retry:
                        logger.warning(f'Waiting for {interface.sleep_timeout} sec...')
                        time.sleep(interface.sleep_timeout)
                        logger.warning('Wake up. Go further...')
                    _tries += 1
        os.remove(path)

    def download(self, locations: List[str], max_retries: int, parallel: bool) -> None:
        """
            Method of downloading data by the locations list
            Depending on the parallel parameter,
            creates and launches a call to the _download method for each requested location line

            :param locations: list of requested strings from which the download request should be made
            :param max_retries: number of max retries
            :param parallel: should be start as parallel or not

            :return:
        """
        if parallel:
            loop = get_event_loop()
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                features = [
                    loop.run_in_executor(
                        executor,
                        self._download,
                        self.get_interface(location)(),
                        location,
                        max_retries
                    ) for location in locations
                ]
                asyncio.wait(features, loop=loop)
        else:
            for location in locations:
                self._download(
                    self.get_interface(location)(),
                    location,
                    max_retries
                )


def init_service():
    """
        Function of init Service
        Available interfaces are registered in this function

        :return: object of initialized Service
    """
    from provider.ftp import FTPDownloadInterface
    from provider.http import (
        HTTPDownloadInterface,
        HTTPsDownloadInterface,
    )
    from provider.sftp import sFTPDownloadInterface

    service = Service()
    service.register_interface(lambda a: a.startswith('http://'), HTTPDownloadInterface)
    service.register_interface(lambda a: a.startswith('https://'), HTTPsDownloadInterface)
    service.register_interface(lambda a: a.startswith('ftp://'), FTPDownloadInterface)
    service.register_interface(lambda a: a.startswith('sftp://'), sFTPDownloadInterface)
    return service
