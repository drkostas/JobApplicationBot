import unittest
import os
import copy
import random
import string
import logging
from typing import List
from mysql.connector.errors import ProgrammingError as MsqlProgrammingError

from configuration.configuration import Configuration
from datastore.mysql_datastore import MySqlDatastore

logger = logging.getLogger('TestMysqlDatastore')


class TestMysqlDatastore(unittest.TestCase):
    __slots__ = ('configuration', 'test_table_schema')

    configuration: Configuration
    test_table_schema: str
    generated_table_names: List[str] = list()
    test_data_path: str = os.path.join('test_data', 'test_mysql_datastore')

    def test_connect(self):
        # Test the connection with the correct api key
        try:
            MySqlDatastore(**self.configuration.get_datastores()[0])
        except MsqlProgrammingError as e:
            logger.error('Error connecting with the correct credentials: %s', e)
            self.fail('Error connecting with the correct credentials')
        else:
            logger.info('Connected with the correct credentials successfully.')
        # Test that the connection is failed with the wrong credentials
        with self.assertRaises(MsqlProgrammingError):
            datastore_conf_copy = copy.deepcopy(self.configuration.get_datastores()[0])
            datastore_conf_copy['password'] = 'wrong_password'
            MySqlDatastore(**datastore_conf_copy)
        logger.info("Loading Mysql with wrong credentials failed successfully.")

    def test_create_drop(self):
        data_store = MySqlDatastore(**self.configuration.get_datastores()[0])
        # Create table
        logger.info('Creating table..')
        data_store.create_table(self.table_name, self.test_table_schema)
        # Check if it was created
        self.assertIn(self.table_name, data_store.show_tables())
        # Drop table
        logger.info('Dropping table..')
        data_store.drop_table(table=self.table_name)
        self.assertNotIn(self.table_name, data_store.show_tables())

    def test_insert_update_delete(self):
        data_store = MySqlDatastore(**self.configuration.get_datastores()[0])
        # Create table
        logger.info('Creating table..')
        data_store.create_table(self.table_name, self.test_table_schema)
        # Ensure it is empty
        results = data_store.select_from_table(table=self.table_name)
        self.assertEqual([], results)
        # Insert into table
        insert_data = {"order_id": 1,
                       "order_type": "plain",
                       "is_delivered": False}
        logger.info("Inserting into table..")
        data_store.insert_into_table(table=self.table_name, data=insert_data)
        # Check if the data was inserted
        results = data_store.select_from_table(table=self.table_name)
        self.assertEqual([(1, "plain", False)], results)
        logger.info("Deleting from table..")
        data_store.delete_from_table(table=self.table_name, where='order_id =1 ')
        # Check if the data was inserted
        results = data_store.select_from_table(table=self.table_name)
        self.assertEqual([], results)

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
        cls.test_table_schema = """ order_id INT(6) PRIMARY KEY,
                                    order_type VARCHAR(30) NOT NULL,
                                    is_delivered BOOLEAN NOT NULL """

    @classmethod
    def tearDownClass(cls):
        data_store = MySqlDatastore(**cls.configuration.get_datastores()[0])
        for table in cls.generated_table_names:
            logger.info('Dropping table {0}'.format(table))
            data_store.drop_table(table=table)


if __name__ == '__main__':
    unittest.main()
