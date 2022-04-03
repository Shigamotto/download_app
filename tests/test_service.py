from unittest import TestCase, mock

from provider.base import BaseDownloadInterface
from service import Service


class TestService(TestCase):

    def test__download(self):
        service = Service()

        mock_open = mock.mock_open()
        with mock.patch.object(
            BaseDownloadInterface, 'get_filepath', side_effect=lambda a: a
        ) as mocked_interface_get_filepath, mock.patch.object(
            BaseDownloadInterface, 'download', return_value=None
        ) as mocked_interface_download,  mock.patch(
            'service.open', mock_open, create=True
        ) as mocked_file, mock.patch(
            'service.os.makedirs'
        ) as mocked_makedirs, mock.patch(
            'service.os.remove'
        ) as mocked_remove:
            service._download(
                BaseDownloadInterface(),
                '<some_path>/<to_download>/<filename>',
                max_retries=0
            )

        mocked_interface_get_filepath.assert_called_once_with('<some_path>/<to_download>/<filename>')
        mocked_file.assert_called_once_with('storage/<some_path>/<to_download>/<filename>', 'wb')
        mocked_makedirs.assert_called_once_with('storage/<some_path>/<to_download>')
        mocked_remove.assert_not_called()

        mocked_file_handle = mock_open()
        mocked_interface_download.assert_called_once_with(mocked_file_handle, '<some_path>/<to_download>/<filename>')

    def test__download_fail_and_call_remove(self):
        service = Service()

        mock_open = mock.mock_open()
        with mock.patch.object(
            BaseDownloadInterface, 'get_filepath', side_effect=lambda a: a
        ) as mocked_interface_get_filepath, mock.patch.object(
            BaseDownloadInterface, 'download', side_effect=ValueError()
        ) as mocked_interface_download,  mock.patch(
            'service.open', mock_open, create=True
        ) as mocked_file, mock.patch(
            'service.os.makedirs'
        ) as mocked_makedirs, mock.patch(
            'service.os.remove'
        ) as mocked_remove:
            service._download(
                BaseDownloadInterface(),
                '<some_path>/<to_download>/<filename>',
                max_retries=0
            )

        mocked_interface_get_filepath.assert_called_once_with('<some_path>/<to_download>/<filename>')
        mocked_file.assert_called_once_with('storage/<some_path>/<to_download>/<filename>', 'wb')
        mocked_makedirs.assert_called_once_with('storage/<some_path>/<to_download>')
        mocked_remove.assert_called_once_with('storage/<some_path>/<to_download>')

        mocked_file_handle = mock_open()
        mocked_interface_download.assert_called_once_with(
            mocked_file_handle, '<some_path>/<to_download>/<filename>'
        )

    def test__download_retries(self):
        service = Service()

        mock_open = mock.mock_open()
        with mock.patch.object(
            BaseDownloadInterface, 'get_filepath', side_effect=lambda a: a
        ) as mocked_interface_get_filepath, mock.patch.object(
            BaseDownloadInterface, 'download', side_effect=ValueError()
        ) as mocked_interface_download,  mock.patch(
            'service.open', mock_open, create=True
        ) as mocked_file, mock.patch(
            'service.os.makedirs'
        ) as mocked_makedirs, mock.patch(
            'service.os.remove'
        ) as mocked_remove:
            service._download(
                BaseDownloadInterface(),
                '<some_path>/<to_download>/<filename>',
                max_retries=3
            )

        mocked_interface_get_filepath.assert_called_once_with('<some_path>/<to_download>/<filename>')
        mocked_file.assert_called_once_with('storage/<some_path>/<to_download>/<filename>', 'wb')
        mocked_makedirs.assert_called_once_with('storage/<some_path>/<to_download>')
        mocked_remove.assert_called_once_with('storage/<some_path>/<to_download>')

        self.assertEqual(4, mocked_interface_download.call_count)
