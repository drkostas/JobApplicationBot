from typing import List
import logging
from gmail import GMail, Message

from .abstract_email_app import AbstractEmailApp


class GmailEmailApp(AbstractEmailApp):
    __slots__ = '_handler'

    _handler: GMail
    logger = logging.getLogger('GmailEmailApp')

    def __init__(self, email_address: str, api_key: str) -> None:
        """
        The basic constructor. Creates a new instance of EmailApp using the specified credentials

        :param api_key:
        """

        self._handler = self.get_handler(email_address=email_address, api_key=api_key)
        super().__init__()

    @staticmethod
    def get_handler(email_address: str, api_key: str) -> GMail:
        """
        Returns an EmailApp handler.

        :param email_address:
        :param api_key:
        :return:
        """

        gmail_handler = GMail(username=email_address, password=api_key)
        gmail_handler.connect()
        return gmail_handler

    def is_connected(self) -> bool:
        return self._handler.is_connected()

    def send_email(self, subject: str, to: List, cc: List = None, bcc: List = None, text: str = None, html: str = None,
                   attachments: List = None, sender: str = None, reply_to: str = None) -> None:
        """
        Sends an email with the specified arguments.

        :param subject:
        :param to:
        :param cc:
        :param bcc:
        :param text:
        :param html:
        :param attachments:
        :param sender:
        :param reply_to:
        :return:
        """

        msg = Message(subject=subject,
                      to=",".join(to),
                      cc=",".join(cc) if cc is not None else None,
                      bcc=",".join(bcc) if cc is not None else None,
                      text=text,
                      html=html,
                      attachments=attachments,
                      sender=sender,
                      reply_to=reply_to)
        self._handler.send(msg)

    def __exit__(self):
        self._handler.close()
