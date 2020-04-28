from typing import Dict, List, Tuple
import logging
from dropbox import Dropbox, files, exceptions

from .dropbox_cloudstore import DropboxCloudstore

logger = logging.getLogger('JobBotDropboxCloudstore')

class JobBotDropboxCloudstore(DropboxCloudstore):
    __slots__ = '_handler'

    _handler: Dropbox

    def __init__(self, api_key: str) -> None:
        """
        The basic constructor. Creates a new instance of JobBotDropboxCloudstore using the specified credentials

        :param api_key:
        """

        super().__init__(api_key=api_key)

    def get_application_email(self) -> Tuple[str, str]:
        raise NotImplementedError()

    def get_inform_should_call_email(self) -> Tuple[str, str]:
        raise NotImplementedError()

    def get_inform_success_email(self) -> Tuple[str, str]:
        raise NotImplementedError()

    def get_stop_words(self) -> List:
        raise NotImplementedError()

    def get_url_search_params(self) -> Dict:
        raise NotImplementedError()

    def update_application_email(self, email: str) -> None:
        raise NotImplementedError()

    def update_inform_should_call_email(self, email: str) -> None:
        raise NotImplementedError()

    def update_inform_success_email(self, email: str) -> None:
        raise NotImplementedError()

    def update_stop_words(self, stop_words: List) -> None:
        raise NotImplementedError()

    def update_url_search_params(self, url_search_params: Dict) -> None:
        raise NotImplementedError()