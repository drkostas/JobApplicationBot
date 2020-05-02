import unittest
import os
import random
import string
import logging
import copy
import ast
from shutil import copyfile
from typing import Tuple
from dropbox.exceptions import BadInputError

from configuration.configuration import Configuration
from cloudstore.job_bot_dropbox_cloudstore import JobBotDropboxCloudstore

logger = logging.getLogger('TestJobBotDropboxCloudstore')


# TODO: Fix ResourceWarning: unclosed file <_io.BufferedReader name='test_data/test_job_bot_dropbox_cloudstore/sample.txt'>
#   open(attachment_path, 'rb').read())
class TestJobBotDropboxCloudstore(unittest.TestCase):
    __slots__ = ('configuration', 'file_name', 'remote_tests_folder')

    configuration: Configuration
    file_name: str
    remote_tests_folder: str
    test_data_path: str = os.path.join('test_data', 'test_job_bot_dropbox_cloudstore')

    def test_init(self):
        req_only_conf = Configuration(
            config_src=os.path.join(self.test_data_path, 'template_conf_required_args_only.yml'))

        cloud_store = JobBotDropboxCloudstore(config=self.configuration.get_cloudstores()[0],
                                              remote_files_folder=self.remote_tests_folder)
        boolean_attributes = [True if len(cloud_store.attachments_names) > 0 else False,
                              cloud_store._update_stop_words,
                              cloud_store._update_application_to_send_email,
                              cloud_store._update_inform_success_email,
                              cloud_store._update_inform_should_call_email]
        self.assertTrue(True, all(boolean_attributes))
        req_only_cloud_store = JobBotDropboxCloudstore(config=req_only_conf.get_cloudstores()[0],
                                                       remote_files_folder=self.remote_tests_folder)
        req_only_boolean_attributes = [True if len(req_only_cloud_store.attachments_names) == 0 else False,
                                       not req_only_cloud_store._update_stop_words,
                                       not req_only_cloud_store._update_application_to_send_email,
                                       not req_only_cloud_store._update_inform_success_email,
                                       not req_only_cloud_store._update_inform_should_call_email]
        self.assertTrue(True, all(req_only_boolean_attributes))

    def test_upload_download_attachment(self):
        cloud_store = JobBotDropboxCloudstore(config=self.configuration.get_cloudstores()[0],
                                              remote_files_folder=self.remote_tests_folder)
        # Copy bck to actual file
        attachment_path = os.path.join(cloud_store.local_files_folder,
                                       cloud_store.attachments_names[0])
        bck_attachment_path = os.path.join(cloud_store.local_files_folder,
                                           'bck_' + cloud_store.attachments_names[0])
        copyfile(bck_attachment_path, attachment_path)
        # Upload attachments
        logger.info('Uploading attachment..')
        cloud_store.upload_attachments()
        # Check if it was uploaded
        self.assertIn(cloud_store.attachments_names[0], cloud_store.ls(self.remote_tests_folder).keys())
        # Rename the old file before downloading it
        logger.info('Renaming the old file before downloading it..')
        os.rename(attachment_path, os.path.join(self.test_data_path, self.file_name))
        # Download it
        logger.info('Downloading attachment..')
        cloud_store.download_attachments()
        # Compare contents of downloaded file with the original
        self.assertEqual(open(os.path.join(self.test_data_path, self.file_name), 'rb').read(),
                         open(attachment_path, 'rb').read())
        # Delete the attachment
        os.remove(attachment_path)

    def test_update_get_stop_words_data(self):
        cloud_store = JobBotDropboxCloudstore(config=self.configuration.get_cloudstores()[0],
                                              remote_files_folder=self.remote_tests_folder)
        # Copy bck to to actual file
        bck_stop_words_path = os.path.join(cloud_store.local_files_folder,
                                           'bck_stop_words.txt')
        stop_words_path = os.path.join(cloud_store.local_files_folder,
                                       'stop_words.txt')
        copyfile(bck_stop_words_path, stop_words_path)
        # Upload stop_words
        logger.info('Uploading stop_words..')
        cloud_store.update_stop_words_data()
        # Check if it was uploaded
        self.assertIn('stop_words.txt', cloud_store.ls(self.remote_tests_folder).keys())
        # Rename the old file before downloading it
        logger.info('Renaming the old file before downloading it..')
        os.rename(os.path.join(self.test_data_path, 'stop_words.txt'),
                  os.path.join(self.test_data_path, self.file_name))
        # Download it
        logger.info('Downloading stop_words..')
        stop_words_downloaded = cloud_store.get_stop_words_data()
        stop_words_downloaded = "['" + "', '".join(stop_words_downloaded) + "']"
        # Compare contents of downloaded file with the original
        self.assertEqual(open(os.path.join(self.test_data_path, self.file_name), 'rb').read(),
                         bytes(stop_words_downloaded, encoding='utf8'))

    def test_update_get_email_data(self):
        cloud_store = JobBotDropboxCloudstore(config=self.configuration.get_cloudstores()[0],
                                              remote_files_folder=self.remote_tests_folder)
        email_types = (('application_to_send', cloud_store.get_application_to_send_email_data,
                        cloud_store.update_application_to_send_email_data),
                       ('inform_should_call', cloud_store.get_inform_should_call_email_data,
                        cloud_store.update_inform_should_call_email_data),
                       ('inform_success', cloud_store.get_inform_success_email_data,
                        cloud_store.update_inform_success_email_data))
        for email_type, get_func, update_func in email_types:
            # Copy bcks to to actual files
            bck_subject_path = os.path.join(cloud_store.local_files_folder,
                                            'bck_subject.txt')
            bck_html_path = os.path.join(cloud_store.local_files_folder,
                                         'bck_body.html')
            current_subject_file = '{type}_subject.txt'.format(type=email_type)
            current_html_file = '{type}_body.html'.format(type=email_type)
            subject_path = os.path.join(cloud_store.local_files_folder,
                                        current_subject_file)
            html_path = os.path.join(cloud_store.local_files_folder,
                                     current_html_file)
            copyfile(bck_subject_path, subject_path)
            copyfile(bck_html_path, html_path)
            # Upload stop_words
            logger.info('Uploading %s email data..' % email_type)
            update_func()
            # Check if it was uploaded
            self.assertIn(current_subject_file, cloud_store.ls(self.remote_tests_folder).keys())
            self.assertIn(current_html_file, cloud_store.ls(self.remote_tests_folder).keys())
            # Rename the old files before downloading them
            logger.info('Renaming the old file before downloading it..')
            copied_subject_file = os.path.join(self.test_data_path,
                                               self.file_name + '_{type}_subject.txt'.format(type=email_type))
            copied_html_file = os.path.join(self.test_data_path,
                                               self.file_name + '_{type}_body.html'.format(type=email_type))
            os.rename(os.path.join(self.test_data_path, current_subject_file), copied_subject_file)
            os.rename(os.path.join(self.test_data_path, current_html_file), copied_html_file)
            # Download it
            logger.info('Downloading {type} email data..'.format(type=email_type))
            actual_subject, actual_html = get_func()
            logger.debug("Received: %s and %s" % (actual_subject, actual_html))
            # Compare contents of downloaded file with the original
            with open(copied_subject_file, 'rb') as f:
                self.assertEqual(f.read(), bytes(actual_subject, encoding='utf-8'))
            with open(copied_html_file, 'rb') as f:
                self.assertEqual(f.read(), bytes(actual_html, encoding='utf-8'))
            logger.info("Clearing file: %s" % copied_subject_file)
            os.remove(copied_subject_file)
            logger.info("Clearing file: %s" % copied_html_file)
            os.remove(copied_html_file)

    @staticmethod
    def _generate_random_filename_and_contents() -> Tuple[str, str]:
        letters = string.ascii_lowercase
        file_name = ''.join(random.choice(letters) for _ in range(10)) + '.txt'
        contents = ''.join(random.choice(letters) for _ in range(20))
        return file_name, contents

    @staticmethod
    def _setup_log() -> None:
        # noinspection PyArgumentList
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.StreamHandler()
                                      ]
                            )

    def setUp(self) -> None:
        self.file_name, contents = self._generate_random_filename_and_contents()
        with open(os.path.join(self.test_data_path, self.file_name), 'a') as f:
            f.write(contents)

    def tearDown(self) -> None:
        os.remove(os.path.join(self.test_data_path, self.file_name))

    @classmethod
    def setUpClass(cls):
        cls._setup_log()
        if "DROPBOX_API_KEY" not in os.environ:
            logger.error('DROPBOX_API_KEY env variable is not set!')
            raise Exception('DROPBOX_API_KEY env variable is not set!')
        logger.info('Loading Configuration..')
        cls.configuration = Configuration(config_src=os.path.join(cls.test_data_path, 'template_conf_all_args.yml'))
        cls.remote_tests_folder = '/job_bot_tests'
        cloud_store = JobBotDropboxCloudstore(config=cls.configuration.get_cloudstores()[0])
        cloud_store.delete_file(cls.remote_tests_folder)

    @classmethod
    def tearDownClass(cls):
        cloud_store = JobBotDropboxCloudstore(config=cls.configuration.get_cloudstores()[0])
        cloud_store.delete_file(cls.remote_tests_folder)


if __name__ == '__main__':
    unittest.main()
