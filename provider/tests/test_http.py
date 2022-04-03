from io import BytesIO
from unittest import TestCase, mock

import responses

from provider.http import HTTPDownloadInterface
from service import init_service


class TestHTTPDownloadInterface(TestCase):

    def test_get_filepath(self):
        interface = HTTPDownloadInterface()
        filepath = interface.get_filepath(
            'https://example.com/filename.exe'
        )
        self.assertEqual('example.com/filename.exe', filepath)

    def test_get_filepath_http(self):
        interface = HTTPDownloadInterface()
        filepath = interface.get_filepath(
            'http://example.com/filename.exe'
        )
        self.assertEqual('example.com/filename.exe', filepath)

    @responses.activate
    def test_download(self):
        interface = HTTPDownloadInterface()
        file = BytesIO()
        responses.add(responses.GET, 'http://example.com/filename.exe', body='body_value')
        interface.download(
            file,
            'http://example.com/filename.exe'
        )
        self.assertEqual(b'body_value', file.getvalue())


class TestDownloadHTTPDownloadInterface(TestCase):

    @responses.activate
    def test(self):
        service = init_service()
        responses.add(responses.GET, 'https://example.com/filename.exe', body='body_value')

        mock_open = mock.mock_open()
        with mock.patch(
            'service.os.makedirs'
        ), mock.patch(
            'service.os.remove'
        ) as mocked_remove, mock.patch(
            'service.open', mock_open, create=True
        ) as mocked_file:
            service.download(['https://example.com/filename.exe'], max_retries=0, parallel=False)

        mocked_file.assert_called_once_with('storage/example.com/filename.exe', 'wb')

        mocked_file_handle = mock_open()
        mocked_file_handle.write.assert_called_once_with(b'body_value')
        mocked_remove.asseert_not_called()
