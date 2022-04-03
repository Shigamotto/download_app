from typing import BinaryIO, Tuple


class BaseDownloadInterface:
    """
        This base class download interface
        All of download interface must be implement from this base class
        All base methods must be implement

        :param retry_on: list of exceptions, which this interface need to retry
        :param sleep_on_retry: bool param if you need pause between retries
        :param sleep_timeout: int: time in seconds of pause between retries
    """

    retry_on: Tuple[BaseException] = (BaseException, )
    sleep_on_retry: bool = False
    sleep_timeout: int = 0

    def get_filepath(self, location) -> str:
        """
            Method of getting filepath from requested location string
            :param location: the requested string from which the download request should be made
            :return: string filepath
        """
        raise NotImplementedError

    def download(self, file: BinaryIO, location: str) -> None:
        """
            Base download method
            It should handle retries and partial downloads
            This means method must be maintain of start downloading from the disconnected byte

            This method can raise any Exception.
            If we need to pass retry on this exception, add this exception to retry_on parameter
            :param file: BinaryIO is the object in which the file will be saved
            :param location: the requested string from which the download request should be made
            :return: Nothing if download complete
        """
        raise NotImplementedError
