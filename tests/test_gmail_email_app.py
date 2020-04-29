import unittest
import os
import random
import string
import logging
from typing import Tuple
from smtplib import SMTPAuthenticationError

from configuration.configuration import Configuration
from email_app.gmail_email_app import GmailEmailApp

logger = logging.getLogger('TestGmailEmailApp')


class TestGmailEmailApp(unittest.TestCase):
    __slots__ = ('configuration', 'file_name')

    configuration: Configuration
    file_name: str
    test_data_path: str = os.path.join('test_data', 'test_gmail_email_app')

    def test_connect(self):
        # Test the connection with the correct api key
        try:
            gmail_configuration = self.configuration.get_email_apps()[0]
            GmailEmailApp(email_address=gmail_configuration['email_address'], api_key=gmail_configuration['api_key'])
        except SMTPAuthenticationError as e:
            logger.error('Error connecting with the correct credentials: %s', e)
            self.fail('Error connecting with the correct credentials')
        else:
            logger.info('Connected with the correct credentials successfully.')
        # Test that the connection is failed with the wrong credentials
        with self.assertRaises(SMTPAuthenticationError):
            GmailEmailApp(email_address=gmail_configuration['email_address'], api_key='wrong_key')
        logger.info("Loading Dropbox with wrong credentials failed successfully.")

    def test_is_connected_and_exit(self):
        gmail_configuration = self.configuration.get_email_apps()[0]
        gmail_app = GmailEmailApp(email_address=gmail_configuration['email_address'],
                                  api_key=gmail_configuration['api_key'])
        self.assertEqual(True, gmail_app.is_connected())
        gmail_app.__exit__()
        self.assertEqual(False, gmail_app.is_connected())

    def test_send_email_with_all_args(self):
        try:
            gmail_configuration = self.configuration.get_email_apps()[0]
            gmail_app = GmailEmailApp(email_address=gmail_configuration['email_address'],
                                      api_key=gmail_configuration['api_key'])

            gmail_app.send_email(subject='test_send_email_with_all_args',
                                 to=[gmail_configuration['email_address']],
                                 cc=[gmail_configuration['email_address']],
                                 bcc=[gmail_configuration['email_address']],
                                 text='Test plain/text body',
                                 html='<h1>Test html body</h1>',
                                 attachments=[os.path.join(self.test_data_path, 'sample_data.txt')],
                                 sender=gmail_configuration['email_address'],
                                 reply_to=gmail_configuration['email_address']
                                 )
        except Exception as e:
            logger.error("Test failed with exception: %s" % e)
            self.fail("Test failed with exception: %s" % e)

    def test_send_email_with_required_args(self):
        try:
            gmail_configuration = self.configuration.get_email_apps()[0]
            gmail_app = GmailEmailApp(email_address=gmail_configuration['email_address'],
                                      api_key=gmail_configuration['api_key'])

            gmail_app.send_email(subject='test_send_email_with_required_args',
                                 to=[gmail_configuration['email_address']]
                                 )
        except Exception as e:
            logger.error("Test failed with exception: %s" % e)
            self.fail("Test failed with exception: %s" % e)

    def test_send_email_with_html(self):
        try:
            gmail_configuration = self.configuration.get_email_apps()[0]
            gmail_app = GmailEmailApp(email_address=gmail_configuration['email_address'],
                                      api_key=gmail_configuration['api_key'])

            gmail_app.send_email(subject='test_send_email_with_html',
                                 to=[gmail_configuration['email_address']],
                                 html='<h1>Html only</h1>'
                                 )
        except Exception as e:
            logger.error("Test failed with exception: %s" % e)
            self.fail("Test failed with exception: %s" % e)

    def test_send_email_with_text(self):
        try:
            gmail_configuration = self.configuration.get_email_apps()[0]
            gmail_app = GmailEmailApp(email_address=gmail_configuration['email_address'],
                                      api_key=gmail_configuration['api_key'])

            gmail_app.send_email(subject='test_send_email_with_text',
                                 to=[gmail_configuration['email_address']],
                                 text='Text only'
                                 )
        except Exception as e:
            logger.error("Test failed with exception: %s" % e)
            self.fail("Test failed with exception: %s" % e)

    @staticmethod
    def _generate_random_filename_and_contents() -> Tuple[str, str]:
        letters = string.ascii_lowercase
        file_name = ''.join(random.choice(letters) for _ in range(10)) + '.txt'
        contents = ''.join(random.choice(letters) for _ in range(20))
        return file_name, contents

    @staticmethod
    def _setup_log(debug: bool = False) -> None:
        # noinspection PyArgumentList
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.StreamHandler()
                                      ]
                            )

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def setUpClass(cls):
        cls._setup_log()
        gmail_os_vars = ['EMAIL_ADDRESS', 'GMAIL_API_KEY']
        if not all(gmail_os_var in os.environ for gmail_os_var in gmail_os_vars):
            logger.error('Gmail env variables are not set!')
            raise Exception('Gmail env variables are not set!')
        logger.info('Loading Configuration..')
        cls.configuration = Configuration(config_src=os.path.join(cls.test_data_path, 'template_conf.yml'))

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
