#####################################################################################################################
#																													#
# Filename: 	WeatherData.py																						#
# Version: 		0.4.3																								#
# Project: 		OpenWeather																							#
# Description: 	SQL operations for WeatherData object.																#
# Creator: 		Berk Acunaş																							#
# Created on: 	2022.06.07																							#
# Last update: 	2024.11.17																							#
#																													#
#																													#
# Class WeatherData																									#
#	private:																										#
# 		- copy(self, other)																							#
# 		- load(self, id)																							#
#	public:																											#
#		- add(self)																									#
#		- add_all(self, rows)
#		- is_exists(self) -> bool																					#
#		- to_list(self) -> list																						#
#																													#
#																													#
# Class WeatherDataCRUD																								#
#	private:																										#
#		- load_tuple(item) -> WeatherData																			#
# 																													#
# 	public:																											#
#		- select(self, id) -> WeatherData																			#
#		- select_all(self) -> list													@staticmethod-like				#
#		- insert(self, weatherData: WeatherData)																	#
#		- insertmany(self, rows)																					#
#		- is_dt_exists(self, weatherData) -> bool																	#
#		- is_hour_of_the_day_existsself, weatherData) -> bool														#
#####################################################################################################################

from MySQLConnection import DBConnection
from LogMe import LogMe, info_message, error_message
from OpenWeatherException import TupleLoadingError


class WeatherData:

	def __init__(self):

		self.id = None
		self.city_id = None
		self.date = None
		self.time = None
		self.weather_type = None
		self.description = None
		self.icon = None
		self.base = None
		self.temperature = None
		self.feels_like = None
		self.temperature_min = None
		self.temperature_max = None
		self.pressure = None
		self.humidity = None
		self.visibility = None
		self.wind_speed = None
		self.wind_degree = None
		self.cloudiness = None
		self.dt = None
		self.sunrise = None
		self.sunset = None
		self.hour_of_the_day = None
		self.logger_id = None

		self.crud = WeatherDataCRUD()

	def copy(self, other):
		'''Copy other object to self object'''

		try:
			self.id = other.id
			self.city_id = other.city_id
			self.date = other.date
			self.time = other.time
			self.weather_type = other.weather_type
			self.description = other.description
			self.icon = other.icon
			self.base = other.base
			self.temperature = other.temperature
			self.feels_like = other.feels_like
			self.temperature_min = other.temperature_min
			self.temperature_max = other.temperature_max
			self.pressure = other.pressure
			self.humidity = other.humidity
			self.visibility = other.visibility
			self.wind_speed = other.wind_speed
			self.wind_degree = other.wind_degree
			self.cloudiness = other.cloudiness
			self.dt = other.dt
			self.sunrise = other.sunrise
			self.sunset = other.sunset
			self.hour_of_the_day = other.hour_of_the_day
			self.logger_id = other.logger_id

		except Exception as error:
			print(error_message('WeatherData.copy()', error))
			self.g_Options.logMe.logs.append(error_message('WeatherData.copy()', error))

	def load(self, id):

		self.copy(self.crud.select(id))

	def add(self):

		self.crud.insert(self)
	
	def add_all(self, rows):

		self.crud.insertmany(rows)

	def is_exists(self) -> bool:
		'''Uses city_id and dt columns for check.'''
		return self.crud.is_dt_exists(self)

	def to_list(self) -> list:

		return [self.city_id, self.date, self.time, self.weather_type, self.description, self.icon, self.base, self.temperature, 
	  			self.feels_like, self.temperature_min, self.temperature_max, self.pressure, self.humidity, self.visibility, 
				self.wind_speed, self.wind_degree, self.cloudiness, self.dt, self.sunrise, self.sunset, self.hour_of_the_day, self.logger_id]


class WeatherDataCRUD:

	def __init__(self):

		self.dbConn = DBConnection()
		self.logMe = LogMe()

	@staticmethod
	def load_tuple(item) -> WeatherData:
		'''Helper function that wraps the operation steps of loading from 
		a database table to a class object. Make assignments from the 
		list object 'item' to the 'self' object.'''

		weatherData = WeatherData()
		try:
			weatherData.id = item[0]
			weatherData.city_id = int(item[1])
			weatherData.date = item[2]
			weatherData.time = item[3]
			weatherData.weather_type = item[4]
			weatherData.description = item[5]
			weatherData.icon = item[6]
			weatherData.base = item[7]
			weatherData.temperature = float(item[8])
			weatherData.feels_like = float(item[9])
			weatherData.temperature_min = float(item[10])
			weatherData.temperature_max = float(item[11])
			weatherData.pressure = int(item[12])
			weatherData.humidity = int(item[13])
			weatherData.visibility = int(item[14])
			weatherData.wind_speed = float(item[15])
			weatherData.wind_degree = int(item[16])
			weatherData.cloudiness = int(item[17])
			weatherData.dt = int(item[18])
			weatherData.sunrise = int(item[19])
			weatherData.sunset = int(item[20])
			weatherData.hour_of_the_day = item[21]
			weatherData.logger_id = int(item[22])

			return weatherData
		
		except Exception as error:
			raise TupleLoadingError(error)

	def select(self, id) -> WeatherData:

		weather_datas = []

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = ''' SELECT id, city_id, date, time, type, description, icon, base, temp, feels_like, temp_min, 
					  temp_max, pressure, humidity, visibility, wind_speed, wind_degree, cloudiness, dt, sunrise, 
					  sunset, hour_of_the_day, logger_id FROM data WHERE id = %s '''
						 
			cur.execute(sql, (id, ))
			row = cur.fetchone()
			cur.close()

			weatherData = None
			if row:
				weatherData = WeatherDataCRUD.load_tuple(row)

				print(info_message('WeatherDataCRUD::select()', 'All weatherdatas are got.'))
				self.logMe.write(info_message('WeatherDataCRUD::select()', 'All weatherdatas are got.'))

			return weatherData

		except Exception as error:
			print(error_message('WeatherDataCRUD::select()', error))
			self.logMe.write(error_message('WeatherDataCRUD::select()', error))

		finally:
			if conn:
				conn.close()

	def select_all(self) -> list:
		
		weather_datas = []

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = ''' SELECT id, city_id, date, time, type, description, icon, base, temp, feels_like, temp_min, temp_max, pressure, 
						humidity, visibility, wind_speed, wind_degree, cloudiness, dt, sunrise, sunset, hour_of_the_day, logger_id FROM data '''
						 
			cur.execute(sql)
			rows = cur.fetchall()
			cur.close()

			if rows:
				for row in rows:
					weatherData = WeatherDataCRUD.load_tuple(row)
					weather_datas.append(weatherData)

				print(info_message('WeatherDataCRUD::select_all()', 'All weatherdatas are got.'))
				self.logMe.write(info_message('WeatherDataCRUD::select_all()', 'All weatherdatas are got.'))

			return weather_datas

		except Exception as error:
			print(error_message('WeatherDataCRUD::select_all()', error))
			self.logMe.write(error_message('WeatherDataCRUD::select_all()', error))

		finally:
			if conn:
				conn.close()

	def insert(self, weatherData: WeatherData):

		try:
			conn = None
			cur = None

			if self.is_dt_exists():
				print(info_message('WeatherDataCRUD::insert()', 'Record already exists.'))
				self.logMe.write(info_message('WeatherDataCRUD::insert()', 'Record already exists.'))
				return

			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = '''INSERT INTO data(city_id, date, time, type, description, icon, base, temp, feels_like, temp_min, 
					    temp_max, pressure, humidity, visibility, wind_speed, wind_degree, cloudiness, dt, sunrise, sunset, hour_of_the_day, logger_id) 
						VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
		
			cur.execute(sql, (self.weatherData.city_id, self.weatherData.date, self.weatherData.time, self.weatherData.weather_type, 
					 	self.weatherData.description, self.weatherData.icon, self.weatherData.base, self.weatherData.temperature, 
						self.weatherData.feels_like, self.weatherData.temperature_min, self.weatherData.temperature_max, 
						self.weatherData.pressure, self.weatherData.humidity, self.weatherData.visibility, self.weatherData.wind_speed, 
						self.weatherData.wind_degree, self.weatherData.cloudiness, self.weatherData.dt, self.weatherData.sunrise, 
						self.weatherData.sunset, self.weatherData.hour_of_the_day, self.weatherData.logger_id))

			cur.close()
			conn.commit()

			print(info_message('WeatherDataCRUD::insert()', 'Weatherdata inserted.'))
			self.logMe.write(info_message('WeatherDataCRUD::insert()', 'Weatherdata inserted.'))
			
		except Exception as error:
			print(error_message('WeatherDataCRUD.insert()', error))
			self.logMe.write(error_message('WeatherDataCRUD.insert()', error))
		
		finally:
			if conn:
				conn.close()
	
	def insertmany(self, rows):

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = '''INSERT INTO data(city_id, date, time, type, description, icon, base, temp, feels_like, temp_min, 
					    temp_max, pressure, humidity, visibility, wind_speed, wind_degree, cloudiness, dt, sunrise, sunset, hour_of_the_day, logger_id) 
						VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
		
			rowCount = cur.executemany(sql, rows)

			cur.close()
			conn.commit()

			print(info_message('WeatherDataCRUD::insertmany()', 'Rows of Weatherdata inserted.'))
			self.logMe.write(info_message('WeatherDataCRUD::insertmany()', 'Weatherdata inserted.'))

			return rowCount

		except Exception as error:
			print(error_message('WeatherDataCRUD.insertmany()', error))
			self.g_Options.logMe.logs.append(error_message('WeatherDataCRUD.insertmany()', error))
		
		finally:
			if conn:
				conn.close()

	def is_dt_exists(self, weatherData) -> bool:
		
		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = 'SELECT COUNT(id) FROM data WHERE city_id = %s AND dt = %s'

			cur.execute(sql, (weatherData.city_id, weatherData.dt))
			row = cur.fetchone()

			if row:
				print(info_message('WeatherDataCRUD::is_dt_exists()', 'Is dt exists checked.'))
				self.logMe.write(info_message('WeatherDataCRUD::is_dt_exists()', 'Is dt exists checked.'))

				return int(row[0]) > 0
			
			return -1

		except Exception as error:
			print(error_message('WeatherDataCRUD.is_dt_exists()', error))
			self.logMe.write(error_message('WeatherDataCRUD.is_dt_exists()', error))

		finally:
			if conn:
				conn.close()

	def is_hour_of_the_day_exists(self, weatherData) -> bool:
		
		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			# qmark style:
			sql = 'SELECT COUNT(id) FROM data WHERE city_id = %s AND date = %s and hour_of_the_day = %s'

			cur.execute(sql, (weatherData.city_id, weatherData.date, weatherData.hour_of_the_day))
			row = cur.fetchone()

			if row:
				print(info_message('WeatherDataCRUD::is_hour_of_the_day_exists()', 'Is hour of the day exists checked.'))
				self.logMe.write(info_message('WeatherDataCRUD::is_hour_of_the_day_exists()', 'Is hour of the day exists checked.'))

				return int(row[0]) > 0
			
			return -1

		except Exception as error:
			print(error_message('WeatherDataCRUD.is_hour_of_the_day_exists()', error))
			self.logMe.write(error_message('WeatherDataCRUD.is_hour_of_the_day_exists()', error))

		finally:
			if conn:
				conn.close()
