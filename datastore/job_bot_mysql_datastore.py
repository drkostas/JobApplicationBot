import logging
from typing import List, Dict

from mysql import connector as mysql_connector

from .mysql_datastore import MySqlDatastore

logger = logging.getLogger('JobBotMySqlDatastore')


class JobBotMySqlDatastore(MySqlDatastore):
    __slots__ = ('_connection', '_cursor', 'application_table_name')

    _connection: mysql_connector.connection_cext.CMySQLConnection
    _cursor: mysql_connector.connection_cext.CMySQLCursor
    application_table_name: str
    application_table_schema: str = 'id int auto_increment primary key, ' \
                                    'link varchar(100) not null, ' \
                                    'email varchar(100) null, ' \
                                    'sent_on varchar(100) not null, ' \
                                    'constraint link unique (link)'

    def __init__(self, username: str, password: str, hostname: str, db_name: str, port: int = 3306,
                 application_table_name: str = 'applications_sent') -> None:
        """
        The basic constructor. Creates a new instance of Datastore using the specified credentials

        :param username:
        :param password:
        :param hostname:
        :param db_name:
        :param port:
        """

        self.application_table_name = application_table_name
        super().__init__(username=username, password=password,
                         hostname=hostname, db_name=db_name, port=port)

    def get_applications_sent(self) -> List[Dict]:
        return self.select_from_table(table=self.application_table_name, columns='id, link, email, sent_on')

    def save_sent_application(self, application_info: Dict) -> None:
        self.insert_into_table(table=self.application_table_name, data=application_info)

    def remove_ad(self, email_id: str) -> None:
        self.delete_from_table(table=self.application_table_name, where='id={email_id}'.format(email_id=email_id))

    def create_applications_sent_table(self) -> None:
        self.create_table(table=self.application_table_name, schema=self.application_table_schema)
