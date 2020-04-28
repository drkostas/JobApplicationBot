from typing import Dict, Any
import logging
from dropbox import Dropbox, files, exceptions

from .abstract_cloudstore import AbstractCloudstore


class DropboxCloudstore(AbstractCloudstore):
    __slots__ = '_handler'

    _handler: Dropbox
    logger = logging.getLogger('DropboxCloudstore')

    def __init__(self, api_key: str) -> None:
        """
        The basic constructor. Creates a new instance of Cloudstore using the specified credentials

        :param api_key:
        """

        self._handler = self.get_handler(api_key=api_key)
        super().__init__()

    @staticmethod
    def get_handler(api_key: str) -> Dropbox:
        """
        Returns a Cloudstore handler.

        :param api_key:
        :return:
        """

        dbx = Dropbox(api_key)
        return dbx

    def upload_file(self, file_stream: bytes, upload_path: str, write_mode: str = 'overwrite') -> None:
        """
        Uploads a file to the Cloudstore

        :param file_stream:
        :param upload_path:
        :param write_mode:
        :return:
        """

        try:
            self._handler.files_upload(f=file_stream, path=upload_path, mode=files.WriteMode(write_mode))
        except exceptions.ApiError as err:
            print('*** API error', err)

    def download_file(self, frompath: str, tofile: str = None) -> Any:
        """
        Downloads a file from the Cloudstore

        :param frompath:
        :param tofile:
        :return:
        """

        try:
            if tofile is not None:
                self._handler.files_download_to_file(download_path=tofile, path=frompath)
            else:
                md, res = self._handler.files_download(path=frompath)
                data = res.content  # The bytes of the file
                return data
        except exceptions.HttpError as err:
            print('*** HTTP error', err)
            return None

    def delete_file(self, file_path: str) -> None:
        """
        Deletes a file from the Cloudstore

        :param file_path:
        :return:
        """

        try:
            self._handler.files_delete_v2(path=file_path)
        except exceptions.ApiError as err:
            print('*** API error', err)

    def ls(self, path: str = '') -> Dict:
        """
        List the files and folders in the Cloudstore

        :param path:
        :return:
        """
        try:
            files_list = self._handler.files_list_folder(path=path)
            files_dict = {}
            for entry in files_list.entries:
                files_dict[entry.name] = entry
            return files_dict
        except exceptions.ApiError as err:
            print('Folder listing failed for', path, '-- assumed empty:', err)
            return {}
