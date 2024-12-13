#####################################################################################################################
#																													#
# Filename: 	City.py																								#
# Version: 		0.4.3																								#
# Project: 		OpenWeather																							#
# Description: 	SQL operations for City object.																		#
# Creator: 		Berk Acunaş																							#
# Created on: 	2022.06.07																							#
# Last update: 	2024.11.13																							#
#																													#
#																													#
# Class City																										#
#	private:																										#
# 		- copy(self, other)																							#
# 		- load(self, id)																							#
#	public:																											#
#		- add(self)																									#
#       - remove(self)																								#
#       - get_id_by_name(self, name) -> int																			#
#       - get_name_by_id(self, id) -> str																			#
#       - get_all(self) -> list																						#
#       - get_all_names(self) -> list																				#
#       - get_all_openweather_ids(self) -> list																		#
#																													#
#																													#
#																													#
# Class CityCRUD																									#
#	private:																										#
#		- load_tuple(item) -> City																					#
#																													#
# 	public:																											#
#		- select(self, id) -> City																					#
#		- select_id_by_name(self, city_name) -> int																	#
#		- select_all(self) -> list													@staticmethod-like				#
#		- select_name_by_id(self, city_id: int) -> str								@staticmethod-like				#
#		- select_all_names(self) -> list											@staticmethod-like				#
#		- select_all_openweather_ids(self) -> list									@staticmethod-like				#
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

import os
from WeatherData import WeatherData
from JsonFile import JsonFile, IJsonFile, decimal_serializer
from MySQLConnection import DBConnection
from LogMe import LogMe, info_message, error_message
from ConfigParserWrapper import ConfigParserWrapper
from OpenWeatherException import TupleLoadingError, TimezoneError

class City():

	def __init__(self):
		
		self.id = None
		self.name = None
		self.longitude = None
		self.latitude = None
		self.country_code = None
		self.timezone = None
		self.openweather_id = None
		self.state = None
  
		self._crud = CityCRUD()
		self._config_wrapper = ConfigParserWrapper()
		self._logMe = LogMe()

		self.weatherDatas = []

	@staticmethod
	def get_last_weather(name: str, state: str | None, country_code: str) -> WeatherData:
	 
		city = City()
		city_id = city.get_id_by_name(name, state, country_code)
		city.load(city_id)
		city._get_last_weather()
  
		return city.weatherDatas[0]

	def _get_last_weather(self):

		weatherData = WeatherData()
		weatherData.get_last(self.id)

		self.weatherDatas.append(weatherData)
  
	def copy(self, other):
		'''Copy other object to self object'''

		try:
			self.id = self._crud.select_id_by_openweather_id(other.openweather_id)
			self.name = other.name
			self.longitude = other.longitude
			self.latitude = other.latitude
			self.country_code = other.country_code
			self.timezone = other.timezone
			self.openweather_id = other.openweather_id
			self.state = other.state

		except Exception as error:
			print(error_message('CityCRUD::copy()', error))
			self._logMe.write(error_message('CityCRUD::copy()', error))
   
		else:
			print(info_message('CityCRUD::copy()', 'City selected.'))
			self._logMe.write(info_message('CityCRUD::copy()', 'City selected.'))

	def load(self, id):

		self.copy(self._crud.select(id))

	def add(self):
		
		self._crud.insert(self)

	def remove(self):

		self._crud.delete(self.id)

	def get_id_by_name(self, name: str, state: str | None, country_code: str) -> int:

		return self._crud.select_id_by_name(name, state, country_code)
	
	def get_name_by_id(self, id) -> str:

		return self._crud.select_name_by_id(id)

	def get_all(self) -> list:

		return self._crud.select_all()

	def get_all_names(self) -> list:

		return self._crud.select_all_names()

	def get_all_openweather_ids(self) -> list:

		return self._crud.select_all_openweather_ids()

	def __str__(self):
		
		s = f'OpenWeather id: {self.openweather_id}, Name: {self.name}, '
		if self.state and self.state != '':
			s += f'State: {self.state} '
		s+= f'Country: {self.country_code}, Longitude: {self.longitude}, Latitude: {self.latitude}'

		return s
	
	def __repr__(self):

		return f'City(\'{self.openweather_id}\', {self.name}, {self.country_code}, {self.longitude}, {self.latitude})'

	def __iter__(self):

		fields = ["id", "name", "longitude", "latitude", "country_code", "timezone", "openweather_id", "state"]
		for key in self.__dict__:
			if key in fields:
				yield key, getattr(self, key)

class CityJson:

	config_wrapper = ConfigParserWrapper()
	search_matches = []
	
	@staticmethod
	def get_matches_proc(item, name: str, state: str | None, country_code: str | None):

		city = None
		if (name == item['name']) and (not state) and (not country_code):
			CityJson.search_matches.append(CityJson._create_match(item))

		elif (name == item['name']) and (state and (state == item['state'])) and (country_code and (country_code == item['country'])):
			CityJson.search_matches.append(CityJson._create_match(item))

		elif (name == item['name']) and (country_code == item['country']) and (not state):
			CityJson.search_matches.append(CityJson._create_match(item))
		
	@staticmethod
	def get_by_openweather_id_proc(item, openweather_id):

		if openweather_id == item['id']:
			CityJson.search_matches.append(CityJson._create_match(item))

	@staticmethod
	def get_openweather_id_proc(item, name: str, state: str | None, country_code: str):
		
		if (name == item['name']) and (country_code == item['country']):
			if (state and (state == item['state'])) or ('state' in item):
				print(f"OpenWeather id: {item['id']} City: {item['name']} State: {item['state']} Country: {item['country']}")
				return
			print(f"OpenWeather id: {item['id']} City: {item['name']} Country: {item['country']}")

	@staticmethod
	def _create_match(item):

		city = City()
		city.openweather_id = item['id']
		city.name = item['name']
		if 'state' in item:
			city.state = item['state']
		city.country_code = item['country']
		city.longitude = item['coord']['lon']
		city.latitude = item['coord']['lat']

		return city
				
	@staticmethod
	def find(city: str | None, state: str | None, country_code: str| None):

		city_list_json = CityJson.config_wrapper.get('OpenWeather.Resources.Json', 'CityList')

		CityJson.search_matches.clear()
		IJsonFile.traverse(CityJson.get_matches_proc, city_list_json, city, state, country_code)

	@staticmethod
	def find_openweather_id(city: str, state: str | None, country_code: str):

		city_list_json = CityJson.config_wrapper.get('OpenWeather.Resources.Json', 'CityList')
		IJsonFile.traverse(CityJson.get_openweather_id_proc, city_list_json, city, state, country_code)

	@staticmethod
	def find_by_openweather_id(openweather_id: int):

		city_list_json = CityJson.config_wrapper.get('OpenWeather.Resources.Json', 'CityList')
		IJsonFile.traverse(CityJson.get_by_openweather_id_proc, city_list_json, openweather_id)

class UserCityJson:

	def __init__(self):

		self.data = {}

		self.config_wrapper = ConfigParserWrapper()
		self.usercity_json_path = self.config_wrapper.get('Data', 'UserCityFile')
		self.load()

	def load(self):

		self.data = JsonFile.load(self.usercity_json_path)

	def save(self):

		JsonFile.save(self.usercity_json_path, self.data, decimal_serializer)

	def __str__(self):
		
		s = ''
		for key, value in self.data.items():
			s += f'{key}: => '
			for k, v in value.items():
				if v is '':
					v = None
				s += f'{k}: {v}  '
			s += '\n'

		return s
	

class CityCRUD():

	def __init__(self):
		
		self.dbConn = DBConnection()
		self._logMe = LogMe()
		
	@staticmethod
	def load_tuple(item) -> City:
		'''Helper function that wraps the operation steps of loading from 
		a database table to a class object. Make assignments from the 
		list object 'item' to the 'self' object.'''

		city = City()
		try:
			city.id = int(item[0])
			city.name = item[1]
			city.longitude = float(item[2])
			city.latitude = float(item[3])
			city.country_code = item[4]
			city.timezone = int(item[5])

			city.openweather_id = 0
			if item[6]:
				city.openweather_id = int(item[6])

			city.state = item[7]

			return city

		except Exception as error:
			raise TupleLoadingError(error)
	
	def select(self, id) -> City:
		
		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT id, name, longitude, latitude, country_code, timezone, openweather_id, state FROM city WHERE id = %s"
			cur.execute(sql, (id, ))
			row = cur.fetchone()
			cur.close()
			
			city = None
			if row:
				city = CityCRUD.load_tuple(row)
	
				print(info_message('CityCRUD::select()', 'City selected.'))
				self._logMe.write(info_message('CityCRUD::select()', 'City selected.'))
	
			return city

		except Exception as error:
			print(error_message('CityCRUD::select()', error))
			self._logMe.write(error_message('CityCRUD::select()', error))
		
		finally:
			if conn:
				conn.close()

	def select_id_by_name(self, name: str, state: str | None, country_code: str) -> int:
		'''If city exists, returns city id from City table.
		  If  city doesn't exist, returns -1.'''

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = None
			if not state:
				sql = "SELECT id FROM city WHERE name = %s AND country_code = %s"
				cur.execute(sql, (name, country_code, ))
			else:
				sql = "SELECT id FROM city WHERE name = %s AND state = %s AND country_code = %s"
				cur.execute(sql, (name, state, country_code, ))
			
			row = cur.fetchone()

			if row:
				print(info_message('CityCRUD::select_id_by_name()', 'City id is got.'))
				self._logMe.write(info_message('CityCRUD::select_id_by_name()', 'City id is got.'))
   
				return int(row[0])

			return -1
			
		except Exception as error:
			print(error_message('CityCRUD::select_id_by_name()', error))
			self._logMe.write(error_message('CityCRUD::select_id_by_name()', error))
		
		finally:
			if conn:
				conn.close()

	def select_name_by_id(self, id: int) -> str:

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT name FROM city WHERE id = %s"
			cur.execute(sql, (id, ))
			row = cur.fetchone()

			print(info_message('CityCRUD::select_name_by_id()', 'City name is got.'))
			self._logMe.write(info_message('CityCRUD::select_name_by_id()', 'City name is got.'))

			if row:
				return str(row[0])

			return None
			
		except Exception as error:
			print(error_message('CityCRUD::select_name_by_id()', error))
			self._logMe.write(error_message('CityCRUD::select_name_by_id()', error))
		
		finally:
			if conn:
				conn.close()
	
	def select_all(self) -> list:
		
		cities = []

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT id, name, longitude, latitude, country_code, timezone, openweather_id, state FROM city"
			cur.execute(sql)
			rows = cur.fetchall()
			cur.close()
			
			if rows:
				for row in rows:
					city = CityCRUD.load_tuple(row)
					cities.append(city)
	 
				print(info_message('CityCRUD::select_all()', 'All cities are got.'))
				self._logMe.write(info_message('CityCRUD::select_all()', 'All cities are got.'))

			return cities
			
		except Exception as error:
			print(error_message('CityCRUD::select_all()', error))
			self._logMe.write(error_message('CityCRUD::select_all()', error))
		
		finally:
			if conn:
				conn.close()

	def select_all_names(self) -> list:
		
		cities = []
		try:
			conn = self.dbConn.createMySQLConnection()
			curr = conn.cursor()

			sql = "SELECT name FROM city"
			curr.execute(sql)

			rows = curr.fetchall()

			if rows:
				for row in rows:
					cities.append(row[0])

			curr.close()
			conn.commit()
   
			print(info_message('CityCRUD::select_all_names()', 'All city names are got.'))
			self._logMe.write(info_message('CityCRUD::select_all_names()', 'All city names are got.'))

			return cities
		
		except Exception as error:
			print(error_message('CityCRUD::select_all_names()', error))
			self._logMe.write(error_message('CityCRUD::select_all_names()', error))
			
		finally:
			if conn:
				conn.close()

	def select_all_openweather_ids(self) -> list:

		openweather_ids = []
		try:
			conn = self.dbConn.createMySQLConnection()
			curr = conn.cursor()

			sql = "SELECT openweather_id FROM city"
			curr.execute(sql)

			rows = curr.fetchall()

			if rows:
				for row in rows:
					openweather_ids.append(row[0])

				print(info_message('CityCRUD::select_all_openweather_ids()', 'All city openweather ids are got.'))
				self._logMe.write(info_message('CityCRUD::select_all_openweather_ids()', 'All city openweather ids are got.'))

			curr.close()
			conn.commit()

			return openweather_ids

		except Exception as error:
			print(error_message('CityCRUD::select_all_openweather_ids()', error))
			self._logMe.write(error_message('CityCRUD::select_all_openweather_ids()', error))

		finally:
			if conn:
				conn.close()

	def insert(self, city: City):
		# inserts into MySQL database
		conn = None

		try:
			if not self.is_exists(self):

				conn = self.dbConn.createMySQLConnection()
				cur = conn.cursor()
				sql = 'INSERT INTO City(name, longitude, latitude, country_code, timezone, openweather_id, state) VALUES(%s, %s, %s, %s, %s, %s, %s)'

				cur.execute(sql, (city.name, city.longitude, city.latitude, city.country_code, city.timezone, city.openweather_id, city.state))

				cur.close()
				conn.commit()
			
		except Exception as error:
			print(error_message('CityCRUD::insert()', error))
			self._logMe.write(error_message('CityCRUD::insert()', error))
   
		else:
			print(info_message('CityCRUD::insert()', 'City inserted.'))
			self._logMe.write(info_message('CityCRUD::insert()', 'City inserted.'))
		
		finally:
			if conn:
				conn.close()

	def update(self, id: int, city: City):

		conn = None
		try:
			
			if not self.is_exists(self):

				conn = self.dbConn.createMySQLConnection()
				cur = conn.cursor()

				sql = ''' UPDATE City SET name = %s, longitude = %s, latitude = %s, country_code = %s, timezone = %s, 
							openweather_id = %s, state = %s WHERE id = %s; '''

				cur.execute(sql, (city.name, city.longitude, city.latitude, city.country_code, city.timezone, city.openweather_id, city.state, id))

				cur.close()
				conn.commit()
			
		except Exception as error:
			print(error_message('CityCRUD::update()', error))
			self._logMe.write(error_message('CityCRUD::update()', error))
   
		else:
			print(info_message('CityCRUD::update()', 'City updated.'))
			self._logMe.write(info_message('CityCRUD::update()', 'City updated.'))
		
		finally:
			if conn:
				conn.close()

	def delete(self, id):
		
		conn = None
		try:
			
			if not self.is_exists(self):

				conn = self.dbConn.createMySQLConnection()
				cur = conn.cursor()
				sql = ''' DELETE FROM city WHERE id = %s; '''

				cur.execute(sql, (id, ))

				cur.close()
				conn.commit()
			
		except Exception as error:
			print(error_message('CityCRUD::delete()', error))
			self._logMe.write(error_message('CityCRUD::delete()', error))
   
		else:
			print(info_message('CityCRUD::delete()', 'City deleted.'))
			self._logMe.write(info_message('CityCRUD::delete()', 'City deleted.'))
		
		finally:
			if conn:
				conn.close()

	def is_exists(self, openweather_id: int) -> bool:
		'''Cannot query by name because there are more than one city with same name. 
		  Use openweather id for query as a unique identifier.'''

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = 'SELECT COUNT(id) FROM city WHERE openweather_id = %s'
			cur.execute(sql, (openweather_id, ))
			row = cur.fetchone()
   
			if row:
				print(info_message('CityCRUD::is_exists()', 'Is city exists checked.'))
				self._logMe.write(info_message('CityCRUD::is_exists()', 'Is city exists checked.'))

				return int(row[0]) > 0

			return -1
			
		except Exception as error:
			print(error_message('CityCRUD::is_exists()', error))
			self._logMe.write(error_message('CityCRUD::is_exists()', error))
   
		finally:
			if conn:
				conn.close()
	
	
	def select_country_by_country_code(self, country_code: str) -> str:
		# Returns the name of country queried by its country code as str

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT country FROM country_code WHERE alpha2_code = ?"
			cur.execute(sql, (country_code, ))
			row = cur.fetchone()
   
			if row:
				print(info_message('CityCRUD::select_country_by_country_code()', 'Country name is got by country code.'))
				self._logMe.write(info_message('CityCRUD::select_country_by_country_code()', 'Country name is got by country code.'))

				return str(row[0])

			return None
				
		except Exception as error:
			print(error_message('CityCRUD::select_country_by_country_code()', error))
			self._logMe.write(error_message('CityCRUD::select_country_by_country_code()', error))
		
		finally:
			if conn:
				conn.close()

	def select_countries(self) -> dict:
		'''Returns all countries and their associated country codes in a dict.'''
		countryDict = {}

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT country, alpha2_code FROM country_code"
			cur.execute(sql)
			rows = cur.fetchall()
			if rows:
				for row in rows:
					countryDict[row[1]] = row[0]
				
				print(info_message('CityCRUD::select_countries()', 'All countries are got into a dictionary.'))
				self._logMe.write(info_message('CityCRUD::select_countries()', 'All countries are got into a dictionary.'))
   
			return countryDict
				
		except Exception as error:
			print(error_message('CityCRUD::select_countries()', error))
			self._logMe.write(error_message('CityCRUD::select_countries()', error))
		
		finally:
			if conn:
				conn.close()


	def select_timezone(self, id: int) -> int:
		'''Returns timezone of city in integer format'''
		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT timezone FROM city WHERE id = %s"
			cur.execute(sql, (id, ))
			row = cur.fetchone()
			cur.close()

			if row:
				print(info_message('CityCRUD::select_timezone()', 'City timezone is got.'))
				self._logMe.write(info_message('CityCRUD::select_timezone()', 'City timezone is got.'))
	   
				timezone = int(row[0])
				timezone = timezone / 3600
				return int(timezone)

			raise TimezoneError('CityCRUD.get_timezone(self, id) -> int => Can\'t get timezone')
				
		except Exception as error:
			print(error_message('CityCRUD::select_timezone()', error))
			self._logMe.write(error_message('CityCRUD::select_timezone()', error))
		
		finally:
			if conn:
				conn.close()

	def insert_timezone_if_not_exists(self, openweather_id: int, timezone: int):

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT COUNT(timezone) FROM city WHERE openweather_id = %s"
			cur.execute(sql, (openweather_id, ))
			row = cur.fetchone()

			if row:
				exists = (int(row[0]) > 0)

				if not exists:
					sql = "UPDATE City SET timezone = %s WHERE id = %s"
					cur.execute(sql, (timezone, openweather_id))

					conn.commit()
					cur.close()
				
		except Exception as error:
			print(error_message('CityCRUD::insert_timezone_if_not_exists()', error))
			self._logMe.write(error_message('CityCRUD::insert_timezone_if_not_exists()', error))
   
		else:
			print(info_message('CityCRUD::insert_timezone_if_not_exists()', 'Timezone is inserted if not exists before.'))
			self._logMe.write(info_message('CityCRUD::insert_timezone_if_not_exists()', 'Timezone is inserted if not exists before.'))
	  
		finally:
			if conn:
				conn.close()


	def select_id_by_openweather_id(self, openweather_id: int) -> int:

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT id FROM city WHERE openweather_id = %s"
			cur.execute(sql, (openweather_id, ))
			row = cur.fetchone()

			if row:
				print(info_message('CityCRUD::select_id_by_openweather_id()', 'City id is got by openweather id.'))
				self._logMe.write(info_message('CityCRUD::select_id_by_openweather_id()', 'City id is got by openweather id.'))

				return str(row[0])

			return -1

		except Exception as error:
			print(error_message('CityCRUD::select_id_by_openweather_id()', error))
			self._logMe.write(error_message('CityCRUD::select_id_by_openweather_id()', error))

		finally:
			if conn:
				conn.close()

	def select_openweather_id_by_id(self, id: int) -> int:

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT openweather_id FROM city WHERE id = %s"
			cur.execute(sql, (id, ))
			row = cur.fetchone()

			if row:
				print(info_message('CityCRUD::select_openweather_id_by_id()', 'City openweather id is got by id.'))
				self._logMe.write(info_message('CityCRUD::select_openweather_id_by_id()', 'City openweather id is got by id.'))

			return str(row[0])

		except Exception as error:
			print(error_message('CityCRUD::select_openweather_id_by_id()', error))
			self._logMe.write(error_message('CityCRUD::select_openweather_id_by_id()', error))

		finally:
			if conn:
				conn.close()

	def select_openweather_id_by_name(self, name: str) -> int:

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT openweather_id FROM city WHERE name = %s"
			cur.execute(sql, (name, ))
			row = cur.fetchone()

			if row:
				print(info_message('CityCRUD::select_openweather_id_by_name()', 'openweather id is got.'))
				self._logMe.write(info_message('CityCRUD::select_openweather_id_by_name()', 'openweather id is got.'))

				return int(row[0])

			return -1
			
		except Exception as error:
			print(error_message('CityCRUD::select_openweather_id_by_name()', error))
			self._logMe.write(error_message('CityCRUD::select_openweather_id_by_name()', error))
		
		finally:
			if conn:
				conn.close()

	def update_openweather_id_by_id(self, openweather_id: int, id: int):

		try:
			conn = self.dbConn.createMySQLConnection()
			cur = conn.cursor()

			sql = 'UPDATE City SET openweather_id = %s WHERE id = %s'

			cur.execute(sql, (openweather_id, id))

			cur.close()
			conn.commit()
			
		except Exception as error:
			print(error_message('CityCRUD::update_openweather_id_by_id()', error))
			self._logMe.write(error_message('CityCRUD::update_openweather_id_by_id()', error))
		
		else:
			print(info_message('CityCRUD::update_openweather_id_by_id()', 'openweather id is updated.'))
			self._logMe.write(info_message('CityCRUD::update_openweather_id_by_id()', 'openweather id is updated.'))
  
		finally:
			if conn:
				conn.close()

