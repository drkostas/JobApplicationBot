import logging
from typing import List, Dict

from mysql import connector as mysql_connector

from .mysql_datastore import MySqlDatastore

logger = logging.getLogger('JobBotMySqlDatastore')

class JobBotMySqlDatastore(MySqlDatastore):
    __slots__ = ('_connection', '_cursor')

    _connection: mysql_connector.connection_cext.CMySQLConnection
    _cursor: mysql_connector.connection_cext.CMySQLCursor

    def __init__(self, username: str, password: str, hostname: str, db_name: str, port: int = 3306) -> None:
        """
        The basic constructor. Creates a new instance of Datastore using the specified credentials

        :param username:
        :param password:
        :param hostname:
        :param db_name:
        :param port:
        """

        super().__init__(username=username, password=password,
                         hostname=hostname, db_name=db_name, port=port)


    def get_ads(self) -> List[Dict]:
        raise NotImplementedError()

    def store_ads(self, email: Dict) -> None:
        raise NotImplementedError()

    def remove_ad(self, email_id: str) -> None:
        raise NotImplementedError()
