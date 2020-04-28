import os
from typing import Dict, List, Tuple
import logging
from dropbox import Dropbox

from .dropbox_cloudstore import DropboxCloudstore

logger = logging.getLogger('JobBotDropboxCloudstore')


class JobBotDropboxCloudstore(DropboxCloudstore):
    __slots__ = ('_handler', 'base_folder')

    _handler: Dropbox
    base_folder: str

    def __init__(self, api_key: str, base_folder: str = 'job_bot_xegr') -> None:
        """
        The basic constructor. Creates a new instance of Cloudstore using the specified credentials

        :param api_key:
        """

        self.base_folder = base_folder
        super().__init__(api_key=api_key)

    def get_application_sent_email_data(self) -> Tuple[str, str]:
        return self._get_email_data(type='application_sent')

    def get_inform_should_call_email_data(self) -> Tuple[str, str]:
        return self._get_email_data(type='inform_should_call')

    def get_inform_success_email_data(self) -> Tuple[str, str]:
        return self._get_email_data(type='inform_success')

    def _get_email_data(self, type: str) -> Tuple[str, str]:
        subject_file_path = os.path.join(self.base_folder, '{type}_subject.txt'.format(type=type))
        html_file_path = os.path.join(self.base_folder, '{type}_html.html'.format(type=type))
        subject_file = self.download_file(frompath=subject_file_path).decode("utf-8")
        html_file = self.download_file(frompath=html_file_path).decode("utf-8")
        return subject_file, html_file

    def get_stop_words(self) -> List:
        stop_words_path = os.path.join(self.base_folder, 'stop_words.txt')
        return list(self.download_file(frompath=stop_words_path))

    def get_url_search_params(self) -> Dict:
        url_search_params_path = os.path.join(self.base_folder, 'url_search_params.txt')
        return dict(self.download_file(frompath=url_search_params_path))

    def update_application_email_data(self, subject: str, body: str) -> None:
        self._update_email_data(subject=subject, body=body, type='application_sent')

    def update_inform_should_call_email_data(self, subject: str, body: str) -> None:
        self._update_email_data(subject=subject, body=body, type='inform_should_call')

    def update_inform_success_email_data(self, subject: str, body: str) -> None:
        self._update_email_data(subject=subject, body=body, type='inform_success')

    def _update_email_data(self, subject: str, body: str, type: str) -> None:
        subject_file_path = os.path.join(self.base_folder, '{type}_subject.txt'.format(type=type))
        html_file_path = os.path.join(self.base_folder, '{type}_html.html'.format(type=type))
        subject_file = subject.encode("utf-8")
        html_file = body.encode("utf-8")
        self.upload_file(file_stream=subject_file, upload_path=subject_file_path)
        self.upload_file(file_stream=html_file, upload_path=html_file_path)

    def update_stop_words(self, stop_words: List) -> None:
        stop_words_path = os.path.join(self.base_folder, 'stop_words.txt')
        stop_words_file = bytes(stop_words)
        self.upload_file(file_stream=stop_words_file, upload_path=stop_words_path)

    def update_url_search_params(self, url_search_params: Dict) -> None:
        url_search_params_path = os.path.join(self.base_folder, 'stop_words.txt')
        url_search_params_file = bytes(url_search_params)
        self.upload_file(file_stream=url_search_params_file, upload_path=url_search_params_path)

    def download_attachments(self, attachment_names: List[str], to_path: str = 'attachments') -> None:
        for attachment_name in attachment_names:
            attachment_local_path = os.path.join(self.base_folder, attachment_name)
            self.download_file(frompath=attachment_local_path, tofile=os.path.join(to_path, attachment_name))

    def upload_attachments(self, attachment_names: List[str], from_path: str = 'attachments') -> None:
        for attachment_name in attachment_names:
            attachment_upload_path = os.path.join(self.base_folder, attachment_name)
            attachment_local_path = os.path.join(from_path, attachment_name)
            with open(attachment_local_path, 'rb') as attachment_file:
                self.upload_file(file_stream=attachment_file.read(), upload_path=attachment_upload_path)
