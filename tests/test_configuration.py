import unittest
from jsonschema.exceptions import ValidationError
from typing import Dict
import logging
import os

from configuration.configuration import Configuration

logger = logging.getLogger('TestConfiguration')


class TestConfiguration(unittest.TestCase):
    test_data_path: str = os.path.join('test_data', 'test_configuration')

    def test_schema_validation(self):
        try:
            logger.info('Loading the correct Configuration..')
            Configuration(config_src=os.path.join(self.test_data_path, 'minimal_conf_correct.yml'),
                          config_schema_path=os.path.join('..', 'tests', self.test_data_path,
                                                          'minimal_yml_schema.json'))
        except ValidationError as e:
            logger.error('Error validating the correct yml: %s', e)
            self.fail('Error validating the correct yml')
        else:
            logger.info('First yml validated successfully.')

        with self.assertRaises(ValidationError):
            logger.info('Loading the wrong Configuration..')
            Configuration(config_src=os.path.join(self.test_data_path, 'minimal_conf_wrong.yml'))
        logger.info('Second yml failed to validate successfully.')

    def test_to_json(self):
        logger.info('Loading Configuration..')
        configuration = Configuration(config_src=os.path.join(self.test_data_path, 'template_conf.yml'))
        expected_json = {'tag': 'production',
                         'test_mode': False,
                         "lookup_url": "www.xe.gr",
                         'datastore': [{'config':
                                            {'hostname': 'host123',
                                             'username': 'user1',
                                             'password': 'pass2',
                                             'db_name': 'db3',
                                             'port': 3306},
                                        'type': 'mysql'}],
                         'cloudstore': [{'config':
                                             {'api_key': 'apiqwerty'},
                                         'type': 'dropbox'}]}
        # Compare
        logger.info('Comparing the results..')
        self.assertDictEqual(self._sort_dict(expected_json), self._sort_dict(configuration.to_json()))

    def test_to_yaml(self):
        logger.info('Loading Configuration..')
        configuration = Configuration(config_src=os.path.join(self.test_data_path, 'template_conf.yml'))
        # Modify and export yml
        logger.info('Changed the host and the api_key..')
        configuration.datastore[0]['config']['hostname'] = 'changedhost'
        configuration.cloudstore[0]['config']['api_key'] = 'changed_api'
        logger.info('Exporting to yaml..')
        configuration.to_yaml('test_data/test_configuration/actual_output_to_yaml.yml')
        # Load the modified yml
        logger.info('Loading the exported yaml..')
        modified_configuration = Configuration(
            config_src=os.path.join(self.test_data_path, 'actual_output_to_yaml.yml'))
        # Compare
        logger.info('Comparing the results..')
        expected_json = {'tag': 'production',
                         'test_mode': False,
                         "lookup_url": "www.xe.gr",
                         'datastore': [{'config':
                                            {'hostname': 'changedhost',
                                             'username': 'user1',
                                             'password': 'pass2',
                                             'db_name': 'db3',
                                             'port': 3306},
                                        'type': 'mysql'}],
                         'cloudstore': [{'config':
                                             {'api_key': 'changed_api'},
                                         'type': 'dropbox'}]}
        self.assertDictEqual(self._sort_dict(expected_json), self._sort_dict(modified_configuration.to_json()))

    @classmethod
    def _sort_dict(cls, dictionary: Dict) -> Dict:
        return {k: cls._sort_dict(v) if isinstance(v, dict) else v
                for k, v in sorted(dictionary.items())}

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

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
