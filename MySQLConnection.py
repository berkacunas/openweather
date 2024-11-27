import os
import re
import shutil
import mysql.connector
from subprocess import Popen, run, PIPE
from ConfigParserWrapper import ConfigParserWrapper
import CryptoSymmetric

from LogMe import LogMe, info_message, error_message, frame_info, print_frame_info

class DbCredentials:

	def __init__(self, host=None, database=None, user=None, password=None, port=3306):
		
		self.host = host
		self.database = database
		self.user = user
		self.password = password
		self.port = port

		self.config_wrapper = ConfigParserWrapper()
		self.secret_key_path = self.config_wrapper.get('Paths', 'SecretKeyFile')

	def load(self):

		secret_key = self.load_secret_key()

		encrypted_host = self.config_wrapper.get('Database.MySQL', 'Host')
		encrypted_database = self.config_wrapper.get('Database.MySQL', 'DbName')
		encrypted_user = self.config_wrapper.get('Database.MySQL', 'Username')
		encrypted_password = self.config_wrapper.get('Database.MySQL', 'Password')
		encrypted_port = self.config_wrapper.get('Database.MySQL', 'Port')

		if (not encrypted_host) or (not encrypted_database) or (not encrypted_user) or (not encrypted_password) or (not encrypted_port):
			return	# At initializing step NULL values are not an error. This func behaves this way is best.
		
		self.host = CryptoSymmetric.decrypt_message(encrypted_host, secret_key)
		self.database = CryptoSymmetric.decrypt_message(encrypted_database, secret_key)
		self.user = CryptoSymmetric.decrypt_message(encrypted_user, secret_key)
		self.password = CryptoSymmetric.decrypt_message(encrypted_password, secret_key)
		self.port = int(CryptoSymmetric.decrypt_message(encrypted_port, secret_key))

	def save(self):

		secret_key = self.load_secret_key()

		encrypted_host = CryptoSymmetric.encrypt_message(self.host, secret_key)
		encrypted_database = CryptoSymmetric.encrypt_message(self.database, secret_key)
		encrypted_user = CryptoSymmetric.encrypt_message(self.user, secret_key)
		encrypted_password = CryptoSymmetric.encrypt_message(self.password, secret_key)
		encrypted_port = CryptoSymmetric.encrypt_message(self.port, secret_key)
		
		self.config_wrapper.set('Database.MySQL', 'Host', encrypted_host.decode('UTF-8'))
		self.config_wrapper.set('Database.MySQL', 'DbName', encrypted_database.decode('UTF-8'))
		self.config_wrapper.set('Database.MySQL', 'Username', encrypted_user.decode('UTF-8'))
		self.config_wrapper.set('Database.MySQL', 'Password', encrypted_password.decode('UTF-8'))
		self.config_wrapper.set('Database.MySQL', 'Port', encrypted_port.decode('UTF-8'))

		self.config_wrapper.write()

	def load_secret_key(self) -> str:

		if os.path.isfile(self.secret_key_path):
			with open(self.secret_key_path, 'rb') as f:
				secret_key = f.read()
				return secret_key
			
		return None


class DBConnection:

	def __init__(self) -> None:

		self.config_wrapper = ConfigParserWrapper()
		self.logMe = LogMe()

		self.db_credentials = DbCredentials()
		self.db_credentials.load()

	def createMySQLConnection(self, no_database=False):

		conn = None

		try:
			if no_database:
				conn = mysql.connector.connect(user = self.db_credentials.user, password = self.db_credentials.password,
											host = self.db_credentials.host)
			else:
				conn = mysql.connector.connect(user = self.db_credentials.user, password = self.db_credentials.password,
											host = self.db_credentials.host, database = self.db_credentials.database)

			print(info_message('DBConnection::createMySQLConnection()', 'Successfully created a connection with MySQL Server.'))
			self.logMe.write(info_message('DBConnection::createMySQLConnection()', 'Successfully created a connection with MySQL Server.'))

			return conn

		except Exception as error:
			print(error_message('DBConnection::createMySQLConnection()', error))
			self.logMe.write(error_message('DBConnection::createMySQLConnection()', error))

		finally:
			if conn:
				conn.close


class DbOptions:

	def __init__(self):
		
		self.config_wrapper = ConfigParserWrapper()
		self.logMe = LogMe()

		self.db_credentials = DbCredentials()
		
	def createDatabase(self, database: str):

		conn = None

		try:
			sql = f'CREATE DATABASE {database}'
			conn = DBConnection().createMySQLConnection(no_database=True)

			cur = conn.cursor()
			cur.execute(sql)
			
			cur.close()
			conn.commit()

		except Exception as error:
			print(error_message('DbOptions::createDatabase()', error))
			self.logMe.write(error_message('DbOptions::createDatabase()', error))
		
		finally:
			if conn:
				conn.close()

	def enableDatabase(self, enable: bool):
		
		self.config_wrapper.set('Database', 'Enabled', enable)
		self.config_wrapper.write()

	def createUser(self, host: str, database: str, user: str, password: str, port: int):

		db_credentials = DbCredentials(host, database, user, password, port)
		db_credentials.save()
	
	def executeSqlFile(self):

		try:
			self.db_schema_path = self.config_wrapper.get('Paths', 'DbSchemaFile')
			self.db_schema_backup_path = self.config_wrapper.get('Paths', 'DbSchemaBackupFile')

			self.db_credentials.load()

			self._edit_dbname_in_sql_script('OpenWeather', self.db_credentials.database)
			
			self.createDatabase(self.db_credentials.database)
			run(f"mysql -u {self.db_credentials.user} -p {self.db_credentials.database} < {self.db_schema_path}", shell=True)

			self.config_wrapper.set('Database', 'Created', True)
			self.config_wrapper.write()

			print(info_message('DbOptions::executeSqlFile()', 'MySQL OpenWeather created.'))
			self.logMe.write(info_message('DbOptions::executeSqlFile()', 'MySQL OpenWeather created.'))

		except Exception as error:
			print(error_message('DbOptions::executeSqlFile()', error))
			self.logMe.write(error_message('DbOptions::executeSqlFile()', error))
	
	def _edit_dbname_in_sql_script(self, old_name: str, new_name: str):

		if not os.path.isfile(self.db_schema_backup_path):
			shutil.copy2(self.db_schema_path, self.db_schema_backup_path)
		else:
			shutil.copy2(self.db_schema_backup_path, self.db_schema_path)

		sql = None
		with open(self.db_schema_path, 'r') as f:
			sql = f.read()

		sql = re.sub(fr'\b{old_name}\b', new_name, sql)

		with open(self.db_schema_path, 'w') as f:
			f.write(sql)

		
		
