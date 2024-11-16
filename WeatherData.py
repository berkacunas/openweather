#####################################################################################################################
#																													#
# Filename: 	WeatherData.py																								#
# Version: 		0.4.3																								#
# Project: 		OpenWeather																							#
# Description: 	SQL operations for WeatherData object.																		#
# Creator: 		Berk Acunaş																							#
# Created on: 	2022.06.07																							#
# Last update: 	2024.11.16																							#
#																													#
#																													#
# Class WeatherData																										#
# 		- copy(self, other)																							#
#																													#
#																													#
# Class WeatherDataCRUD																									#
#	private:																										#
#		- load_tuple(item) -> WeatherData																					#
#		- load(self, id)
# 																											#
# 	public:																											#
#		- select(self, id) -> City																					#
#		- select_id_by_name(self, city_name) -> int																	#
#		- select_all(self) -> list													@staticmethod-like				#
#		- select_name_by_id(self, city_id: int) -> str								@staticmethod-like				#
#		- select_all_names(self) -> list											@staticmethod-like				#
#		- insert(self, city: City)																					#
#		- update(self, id: int, city: City)																			#
#		- delete(self, id)																							#
#		- is_exists(self, openweather_id) -> bool									@staticmethod-like				#
#																													#
#		- select_country_by_country_code(self, country_code: str) -> str			@staticmethod-like				#
#		- select_countries(self) -> dict											@staticmethod-like				#
#																													#
#		- select_timezone(self, id: int) -> int										@staticmethod-like				#
#		- insert_timezone_if_not_exists(self, openweather_id: int, timezone: int)	@staticmethod-like				#
#																													#
#		- select_id_by_openweather_id(self, openweather_id: int) -> int				@staticmethod-like				#
#		- select_openweather_id_by_name(self, name: str) -> int						@staticmethod-like				#
#		- update_openweather_id_by_id(self, openweather_id: int, id: int)			@staticmethod-like				#
#																													#
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
			# self.query_id = other.query_id

		except Exception as error:
			print(error_message('WeatherData.copy()', error))
			self.g_Options.logMe.logs.append(error_message('WeatherData.copy()', error))


class WeatherDataCRUD:

	def __init__(self):

		self.dbConn = DBConnection()
		self.logMe = LogMe()
		self.query_id = None

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
			# self.query_id = item[22]

			return weatherData
		
		except Exception as error:
			raise TupleLoadingError(error)


	def select_all(self) -> list:
		
		weather_datas = []

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = ''' SELECT id, city_id, date, time, type, description, icon, base, temp, feels_like, temp_min, temp_max, pressure, 
						humidity, visibility, wind_speed, wind_degree, cloudiness, dt, sunrise, sunset, hour_of_the_day, query_id FROM data '''
						 
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
