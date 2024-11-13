import mysql.connector
from configparser import ConfigParser

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

		config = ConfigParser()
		config.read('serviceconfig.ini')

		self.logMe = LogMe()

		self.db_conn_parameter = DbConnParameter()
		self.db_conn_parameter.host = config.get('Database.MySQL', 'Host')
		self.db_conn_parameter.database = config.get('Database.MySQL', 'DbName')
		self.db_conn_parameter.user = config.get('Database.MySQL', 'Username')
		self.db_conn_parameter.password = config.get('Database.MySQL', 'Password')
		

	def createMySQLConnection(self):

		conn = None

		try:
			conn = mysql.connector.connect(user = self.db_conn_parameter.user, password = self.db_conn_parameter.password,
											host = self.db_conn_parameter.host, database = self.db_conn_parameter.database)

			print(info_message('DBConnection::createMySQLConnection()', 'Successfully created a connection with MySQL Server.'))
			self.logMe.write(info_message('DBConnection::createMySQLConnection()', 'Successfully created a connection with MySQL Server.'))

			return conn

		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.logMe.write(error_message(print_frame_info(fi), error))

			#self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
			#raise Exception(error_message('DBConnection.createMySQLConnection(self, db_conn_parameter: DbConnParameter = None)', error))

		finally:
			if conn:
				conn.close

	
