# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from datetime import datetime


class DataStore():
	def __init__(self, user, password, hostname, dbname):
		"""Creates a new instance of the data store using the specified schema

		Args:
			db_path (str): The path where the database should be stored
			schema_path (str): The path to the SQL schema of the database
		"""

		self.engine = create_engine("mysql://{}:{}@{}/{}".format(user, password, hostname, dbname))
		self.session_obj = sessionmaker(bind=self.engine)
		self.session = scoped_session(self.session_obj)


	def __exit__(self):
		self.session.flush()
		self.session.commit()


	def email_from_row(self, row):
		"""Transform a database row into a email representation

		Args:
			row (list): The database row
		"""
		email = dict()
		email['id'] = row[0]
		email['link'] = row[1]
		email['address'] = row[2]
		email['sent_on'] = row[3]
		return email


	def row_from_link(self, email):
		"""Transform a email object into a database row

		Args:
			email (dict): The email object
		"""
		return (email['link'], email['address'], email['sent_on'])


	def store_ads(self, email):
		"""Insert the provided email object into the database"""
		session = self.session
		session.execute('INSERT INTO email VALUES (NULL, "{}", "{}", "{}")'.format(*self.row_from_link(email)))
		session.commit()


	def get_ad_by_id(self, id):
		"""Retrieve a email from the database by its ID

		Args:
			id (str): The email ID
		"""
		session = self.session
		result = session.execute('SELECT * FROM email WHERE id = {}'.format(id)).fetchone()
		if result is not None:
			return self.email_from_row(result)
		return None


	def get_ad_by_address(self, address):
		"""Retrieve a email from the database by its email

		Args:
			id (str): The email of the email owner
		"""
		session = self.session
		result = session.execute('SELECT * FROM email WHERE address = {}'.format(address)).fetchone()
		if result is not None:
			return self.email_from_row(result)
		return None

	def get_ads(self):
		"""Retrieve all emails from the database"""
		session = self.session
		for row in session.execute('SELECT * FROM email'):
			yield self.email_from_row(row)
		return None

	def remove_ad(self, email):
		"""Remove a email from the database

		Args:
			email (dict): The email to be removed (by key 'id')
		"""
		session = self.session
		session.execute('DELETE FROM email WHERE id = {}'.format(email['id']))
		session.commit()

	def update_last_checked(self, email_id):
		"""Update the last_checked value of a specific email

		Args:
			email_id (str): The email to be updated
		"""
		session = self.session
		sessions.execute('UPDATE email SET last_checked = {} WHERE id = {}'.format(datetime.utcnow().isoformat(), email_id))
		session.commit()
