import platform

from datetime import datetime

from MySQLConnection import DBConnection
from LogMe import LogMe, info_message, error_message, frame_info, print_frame_info
from OpenWeatherException import OpenWeatherLoggerNotMarkedError

class OpenWeatherLogger:
	
	def __init__(self, query_string=None, query_date=None, query_time=None, dt=None, username=None, 
			  computer_name=None, system_os=None, python_version=None):
		
		self.is_marked = False

		self.id = None
		self.query_string = query_string
		self.query_date = query_date
		self.query_time = query_time
		self.dt = dt
		self.username = username
		if (not computer_name): self.computer_name = platform.node()
		if (not system_os): self.system_os = platform.platform()
		if (not python_version): self.python_version = platform.python_version()

		self.crud = OpenWeatherLoggerCRUD()
		
	def mark(self, dt, query_string, NOW):

		self.query_string = query_string	# aka 'url'
		self.dt = dt						# first_data_dt = int(datalist['list'][0]["dt"])
		self.query_date = NOW.date().strftime('%Y.%m.%d')
		self.query_time = NOW.time().strftime('%H:%M.%S')
		self.hourly_query = f'{NOW.date().year}-{NOW.date().month}-{NOW.date().day}-{NOW.time().hour}'

		self.is_marked = True

	def add(self) -> int:
		'''Returns id of added record.'''
		if self.is_marked:
			self.crud.insert(self)
			self.is_marked = False
			return self.crud.select_id(self.dt, self.query_time)
		else:
			raise OpenWeatherLoggerNotMarkedError()


class OpenWeatherLoggerCRUD():

	def __init__(self):

		self.dbConn = DBConnection()
		self.logMe = LogMe()

	def insert(self, logger: OpenWeatherLogger):

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = '''INSERT INTO log(hourly_query, query_string, query_date, query_time, dt, username, computer_name, system_os, python_version) 
								VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) '''
		
			cur.execute(sql, (logger.hourly_query, logger.query_string, logger.query_date, logger.query_time, self.dt, self.username, self.computer_name, 
								logger.system_os, logger.python_version))

			cur.close()
			conn.commit()

			print(info_message('OpenWeatherLoggerCRUD::insert()', 'OpenWeather query logged.'))
			self.logMe.write(info_message('OpenWeatherLoggerCRUD::insert()', 'OpenWeather query logged.'))
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.logMe.write(error_message(print_frame_info(fi), error))
		
		finally:
			if conn:
				conn.close()

	def select_last_hourly_query(self) -> str:

		hourly_query = ''
		
		try:
			conn = self.dbConn.createMySQLConnection()
			curr = conn.cursor()

			sql = ''' SELECT hourly_query FROM log ORDER BY id DESC LIMIT 1 '''

			curr.execute(sql)
			row = curr.fetchone()

			curr.close()

			if row:
				hourly_query = row[0]

				print(info_message('OpenWeatherLoggerCRUD::select_last_hourly_query()', 'Last hourly query selected.'))
				self.logMe.write(info_message('OpenWeatherLoggerCRUD::select_last_hourly_query()', 'Last hourly query selected.'))
					
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.logMe.write(error_message(print_frame_info(fi), error))

		finally:
			if conn:
				conn.close()

		return hourly_query

	def select_id(self, dt: int, query_time: int) -> int:
		
		id = None
		try:
			conn = self.dbConn.createMySQLConnection()
			curr = conn.cursor()

			sql = ''' SELECT id FROM log WHERE dt = %s AND query_time = %s '''

			curr.execute(sql, (dt, query_time, ))
			row = curr.fetchone()

			curr.close()

			if row:
				print(info_message('OpenWeatherLoggerCRUD::select_id()', 'Id selected.'))
				self.logMe.write(info_message('OpenWeatherLoggerCRUD::select_id()', 'Id selected.'))

				return int(row[0])
			
			return -1
					
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.logMe.write(error_message(print_frame_info(fi), error))

		finally:
			if conn:
				conn.close()

		return id

