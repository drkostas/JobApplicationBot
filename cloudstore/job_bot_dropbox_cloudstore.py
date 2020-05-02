import os
from typing import Dict, List, Tuple
import logging
import ast
from dropbox import Dropbox

from .dropbox_cloudstore import DropboxCloudstore

logger = logging.getLogger('JobBotDropboxCloudstore')


class JobBotDropboxCloudstore(DropboxCloudstore):
    __slots__ = ('_handler', 'remote_files_folder', 'local_files_folder',
                 'attachments_names', '_update_attachments', '_update_stop_words',
                 '_update_application_to_send_email', '_update_inform_success_email', '_update_inform_should_call_email')

    _handler: Dropbox
    remote_files_folder: str
    local_files_folder: str
    attachments_names: List
    _update_attachments: bool
    _update_stop_words: bool
    _update_application_to_send_email: bool
    _update_inform_success_email: bool
    _update_inform_should_call_email: bool

    def __init__(self, config: Dict, remote_files_folder: str = '/job_bot_xegr') -> None:
        """
        The basic constructor. Creates a new instance of Cloudstore using the specified credentials

        :param config:
        """

        self.remote_files_folder = remote_files_folder
        self.local_files_folder = config['local_files_folder']
        # Set default value for attachments_names
        self.attachments_names = config[
            'attachments_names'] if 'attachments_names' in config else []
        # Default value for the boolean attributes is False
        self._update_attachments = config[
            'update_attachments'] if 'update_attachments' in config else False
        self._update_stop_words = config[
            'update_stop_words'] if 'update_stop_words' in config else False
        self._update_application_to_send_email = config[
            'update_application_to_send_email'] if 'update_application_to_send_email' in config else False
        self._update_inform_success_email = config[
            'update_inform_success_email'] if 'update_inform_success_email' in config else False
        self._update_inform_should_call_email = config[
            'update_inform_should_call_email'] if 'update_inform_should_call_email' in config else False
        super().__init__(config=config)

    def get_application_to_send_email_data(self) -> Tuple[str, str]:
        return self._get_email_data(type='application_to_send')

    def get_inform_should_call_email_data(self) -> Tuple[str, str]:
        return self._get_email_data(type='inform_should_call')

    def get_inform_success_email_data(self) -> Tuple[str, str]:
        return self._get_email_data(type='inform_success')

    def get_stop_words_data(self) -> List[str]:
        stop_words_path = os.path.join(self.remote_files_folder, 'stop_words.txt')
        return eval(self.download_file(frompath=stop_words_path))

    def _get_email_data(self, type: str) -> Tuple[str, str]:
        subject_file_path = os.path.join(self.remote_files_folder, '{type}_subject.txt'.format(type=type))
        html_file_path = os.path.join(self.remote_files_folder, '{type}_body.html'.format(type=type))
        subject_file = self.download_file(frompath=subject_file_path).decode("utf-8")
        html_file = self.download_file(frompath=html_file_path).decode("utf-8")
        return subject_file, html_file

    def download_attachments(self) -> None:
        for attachment_name in self.attachments_names:
            attachment_local_path = os.path.join(self.local_files_folder, attachment_name)
            attachment_remote_path = os.path.join(self.remote_files_folder, attachment_name)
            self.download_file(frompath=attachment_remote_path, tofile=attachment_local_path)

    def update_application_to_send_email_data(self) -> None:
        if self._update_application_to_send_email:
            self._update_email_data(type='application_to_send')
        else:
            logger.info("The update of application_to_send email data was skipped.")

    def update_inform_should_call_email_data(self) -> None:
        if self._update_inform_should_call_email:
            self._update_email_data(type='inform_should_call')
        else:
            logger.info("The update of inform_should_call email data was skipped.")

    def update_inform_success_email_data(self) -> None:
        if self._update_inform_success_email:
            self._update_email_data(type='inform_success')
        else:
            logger.info("The update of inform_success email data was skipped.")

    def update_stop_words_data(self, stop_words_local_file_name: str = 'stop_words.txt') -> None:
        if self._update_stop_words:
            stop_words_remote_path = os.path.join(self.remote_files_folder, 'stop_words.txt')
            stop_words_local_path = os.path.join(self.local_files_folder, stop_words_local_file_name)
            with open(stop_words_local_path, 'rb') as stop_words_file:
                self.upload_file(file_bytes=stop_words_file.read(), upload_path=stop_words_remote_path)
        else:
            logger.info("The update of stop_words data was skipped.")

    def _update_email_data(self, type: str) -> None:
        logger.info("Updating the %s email data.." % type)
        subject_remote_path = os.path.join(self.remote_files_folder, '{type}_subject.txt'.format(type=type))
        html_remote_path = os.path.join(self.remote_files_folder, '{type}_body.html'.format(type=type))
        subject_local_path = os.path.join(self.local_files_folder, '{type}_subject.txt'.format(type=type))
        html_local_path = os.path.join(self.local_files_folder, '{type}_body.html'.format(type=type))
        with open(subject_local_path, 'rb') as subject_file:
            self.upload_file(file_bytes=subject_file.read(), upload_path=subject_remote_path)
        with open(html_local_path, 'rb') as html_file:
            self.upload_file(file_bytes=html_file.read(), upload_path=html_remote_path)

    def upload_attachments(self) -> None:
        if self._update_attachments:
            for attachment_name in self.attachments_names:
                attachment_upload_path = os.path.join(self.remote_files_folder, attachment_name)
                attachment_local_path = os.path.join(self.local_files_folder, attachment_name)
                with open(attachment_local_path, 'rb') as attachment_file:
                    self.upload_file(file_bytes=attachment_file.read(), upload_path=attachment_upload_path)
