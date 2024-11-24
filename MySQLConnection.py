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

		config_wrapper = ConfigParserWrapper()
		self.logMe = LogMe()

		self.db_conn_parameter = DbConnParameter()
		self.db_conn_parameter.host = config_wrapper.get('Database.MySQL', 'Host')
		self.db_conn_parameter.database = config_wrapper.get('Database.MySQL', 'DbName')
		self.db_conn_parameter.user = config_wrapper.get('Database.MySQL', 'Username')
		self.db_conn_parameter.password = config_wrapper.get('Database.MySQL', 'Password')
		self.db_schema_path = config_wrapper.get('Paths', 'DbSchemaFile')

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

	def isDatabaseExists(self, db_name):

		conn = None

		try:
			conn = self.createMySQLConnection()
			curr = conn.cursor()

			sql = 'SHOW DATABASES;'

			curr.execute(sql)
			rows = curr.fetchall()

			if rows:
				print(info_message('DBConnection::isDatabaseExists()', 'Checked database exists.'))
				self.logMe.write(info_message('DBConnection::isDatabaseExists()', 'Checked database exists.'))

				for row in rows:
					if db_name == row[0]:
						return True
					
			return False

		except Exception as error:
			print(error_message('DBConnection::isDatabaseExists()', error))
			self.logMe.write(error_message('DBConnection::isDatabaseExists()', error))



	def executeSqlFile(self, db_username=None):

		if not db_username:
			db_username = self.db_conn_parameter.user

		try:
			run(f"mysql -u {db_username} -p {self.db_conn_parameter.database} < {self.db_schema_path}", shell=True)

			print(info_message('DBConnection::executeSqlFile()', 'MySQL OpenWeather created.'))
			self.logMe.write(info_message('DBConnection::executeSqlFile()', 'MySQL OpenWeather created.'))

		except Exception as error:
			print(error_message('DBConnection::executeSqlFile()', error))
			self.logMe.write(error_message('DBConnection::executeSqlFile()', error))
	