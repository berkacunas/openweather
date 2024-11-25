import mysql.connector
from subprocess import Popen, run, PIPE
from ConfigParserWrapper import ConfigParserWrapper

from LogMe import LogMe, info_message, error_message, frame_info, print_frame_info

class DbConnParameter:

	def __init__(self):

		self.user = None
		self.password = None
		self.host = None
		self.port = None
		self.database = None

class DBConnection:

	def __init__(self) -> None:

		self.config_wrapper = ConfigParserWrapper()
		self.logMe = LogMe()

		self.setCredentials()

	def setCredentials(self):

		self.db_conn_parameter = DbConnParameter()
		self.db_conn_parameter.host = self.config_wrapper.get('Database.MySQL', 'Host')
		self.db_conn_parameter.database = self.config_wrapper.get('Database.MySQL', 'DbName')
		self.db_conn_parameter.user = self.config_wrapper.get('Database.MySQL', 'Username')
		self.db_conn_parameter.password = self.config_wrapper.get('Database.MySQL', 'Password')

	def createMySQLConnection(self):

		conn = None

		try:
			conn = mysql.connector.connect(user = self.db_conn_parameter.user, password = self.db_conn_parameter.password,
											host = self.db_conn_parameter.host, database = self.db_conn_parameter.database)

			print(info_message('DBConnection::createMySQLConnection()', 'Successfully created a connection with MySQL Server.'))
			self.logMe.write(info_message('DBConnection::createMySQLConnection()', 'Successfully created a connection with MySQL Server.'))

			return conn

		except Exception as error:
			print(error_message('DBConnection::createMySQLConnection()', error))
			self.logMe.write(error_message('DBConnection::createMySQLConnection()', error))

		finally:
			if conn:
				conn.close

class DbCreator:

	def __init__(self):
		
		self.config_wrapper = ConfigParserWrapper()
		self.logMe = LogMe()

		self.db_conn_parameter = DbConnParameter()
		self.db_conn_parameter.host = self.config_wrapper.get('Database.MySQL', 'Host')
		self.db_conn_parameter.database = self.config_wrapper.get('Database.MySQL', 'DbName')
		self.db_conn_parameter.user = self.config_wrapper.get('Database.MySQL', 'Username')
		self.db_conn_parameter.password = self.config_wrapper.get('Database.MySQL', 'Password')

		self.db_schema_path = self.config_wrapper.get('Paths', 'DbSchemaFile')

	def createUserLogin(self, host, database, user, password):

		self.config_wrapper.set('Database.MySQL', 'Host', host)
		self.config_wrapper.set('Database.MySQL', 'DbName', database)
		self.config_wrapper.set('Database.MySQL', 'Username', user)
		self.config_wrapper.set('Database.MySQL', 'Password', password)
		self.config_wrapper.write()
	
	def executeSqlFile(self):

		try:
			run(f"mysql -u {self.db_conn_parameter.user} -p {self.db_conn_parameter.database} < {self.db_schema_path}", shell=True)

			print(info_message('DbCreator::executeSqlFile()', 'MySQL OpenWeather created.'))
			self.logMe.write(info_message('DbCreator::executeSqlFile()', 'MySQL OpenWeather created.'))

		except Exception as error:
			print(error_message('DbCreator::executeSqlFile()', error))
			self.logMe.write(error_message('DbCreator::executeSqlFile()', error))
	