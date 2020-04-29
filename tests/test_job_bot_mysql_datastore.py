import unittest
import os
import datetime
import random
import string
import logging
from typing import List


from configuration.configuration import Configuration
from datastore.job_bot_mysql_datastore import JobBotMySqlDatastore

logger = logging.getLogger('TestJobBotMysqlDatastore')


class TestJobBotMysqlDatastore(unittest.TestCase):
    __slots__ = ('configuration', 'test_table_schema')

    configuration: Configuration
    test_table_schema: str
    generated_table_names: List[str] = list()
    test_data_path: str = os.path.join('test_data', 'test_job_bot_mysql_datastore')


    def test_create_applications_sent_table(self):
        data_store = JobBotMySqlDatastore(config=self.configuration.get_datastores()[0],
                                          application_table_name=self.table_name)
        # Check if table not exists
        self.assertNotIn(self.table_name, data_store.show_tables())
        # Create applications sent table
        logger.info('Creating applications sent table..')
        data_store.create_applications_sent_table()
        # Check if it was created
        self.assertIn(self.table_name, data_store.show_tables())
        # Drop table
        logger.info('Dropping table..')
        data_store.drop_table(table=self.table_name)
        # Check if it was deleted
        self.assertNotIn(self.table_name, data_store.show_tables())

    def test_save_sent_application(self):
        data_store = JobBotMySqlDatastore(config=self.configuration.get_datastores()[0],
                                          application_table_name=self.table_name)
        # Create applications sent table
        logger.info('Creating applications sent table..')
        data_store.create_applications_sent_table()
        # Check if it is empty
        self.assertListEqual([], data_store.select_from_table(table=self.table_name))
        # Insert a row
        datetime_now = datetime.datetime.utcnow().isoformat()
        row = {'link': 'www.test.com',
               'email': 'test@test.com',
               'sent_on': datetime_now}
        logger.info('Inserting row into applications sent table..')
        data_store.save_sent_application(row)
        # Check if row was inserted
        self.assertListEqual([(1, 'www.test.com', 'test@test.com', datetime_now)],
                             data_store.select_from_table(table=self.table_name))

    def test_get_applications_sent(self):
        data_store = JobBotMySqlDatastore(config=self.configuration.get_datastores()[0],
                                          application_table_name=self.table_name)
        # Create applications sent table
        logger.info('Creating applications sent table..')
        data_store.create_applications_sent_table()
        # Insert to rows
        datetime_now = datetime.datetime.utcnow().isoformat()
        row1 = {'link': 'www.test1.com',
               'email': 'test1@test1.com',
               'sent_on': datetime_now}
        row2 = {'link': 'www.test2.com',
                'email': 'test2@test2.com',
                'sent_on': datetime_now}
        logger.info('Inserting two rows into applications sent table..')
        data_store.save_sent_application(row1)
        data_store.save_sent_application(row2)
        logger.info('Getting the two rows using the get_applications_sent()..')
        expected_result = [tuple(row1.values()), tuple(row2.values())]
        # Check if they were inserted
        self.assertListEqual(sorted(expected_result),
                             sorted([result[1:] for result in data_store.get_applications_sent()]))

    def test_remove_ad(self):
        data_store = JobBotMySqlDatastore(config=self.configuration.get_datastores()[0],
                                          application_table_name=self.table_name)
        # Create applications sent table
        logger.info('Creating applications sent table..')
        data_store.create_applications_sent_table()
        # Insert to rows
        datetime_now = datetime.datetime.utcnow().isoformat()
        row1 = {'link': 'www.test1.com',
               'email': 'test1@test1.com',
               'sent_on': datetime_now}
        row2 = {'link': 'www.test2.com',
                'email': 'test2@test2.com',
                'sent_on': datetime_now}
        logger.info('Inserting two rows into applications sent table..')
        data_store.save_sent_application(row1)
        data_store.save_sent_application(row2)
        logger.info('Deleting the first row from the applications sent table..')
        data_store.remove_ad(email_id=1)
        logger.info('Getting the remaining row using the get_applications_sent()..')
        expected_result = [tuple(row2.values())]
        # Check if they were inserted
        self.assertListEqual(sorted(expected_result),
                             sorted([result[1:] for result in data_store.get_applications_sent()]))



    @staticmethod
    def _generate_random_filename() -> str:
        letters = string.ascii_lowercase
        file_name = 'test_table_' + ''.join(random.choice(letters) for _ in range(10))
        return file_name

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
        self.table_name = self._generate_random_filename()
        self.generated_table_names.append(self.table_name)

    def tearDown(self) -> None:
        pass

    @classmethod
    def setUpClass(cls):
        cls._setup_log()
        mysql_os_vars = ['MYSQL_HOST', 'MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_DB_NAME']
        if not all(mysql_os_var in os.environ for mysql_os_var in mysql_os_vars):
            logger.error('Mysql env variables are not set!')
            raise Exception('Mysql env variables are not set!')
        logger.info('Loading Configuration..')
        cls.configuration = Configuration(config_src=os.path.join(cls.test_data_path, 'template_conf.yml'))


    @classmethod
    def tearDownClass(cls):
        data_store = JobBotMySqlDatastore(config=cls.configuration.get_datastores()[0])
        for table in cls.generated_table_names:
            logger.info('Dropping table {0}'.format(table))
            data_store.drop_table(table=table)


if __name__ == '__main__':
    unittest.main()
