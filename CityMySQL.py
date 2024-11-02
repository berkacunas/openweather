#############################################################################################################
# Filename: CityMySQL.py
# Version: 0.4.3
# Project: OpenWeather
# Description: SQL operations for City object.
# Creator: Berk Acunaş
# Created on: 2022.06.07
# Methods:
# private:
#	- load_tuple(self, item)
#	- copy(self, other)
# public:
#	- select(self)
#	- select_id(self)
#	- insert(self)
#	- update(self)
#	- delete(self)
#	- get_all(self) -> list												@staticmethod-like
#	- get_name(self, city_id: int) -> str								@staticmethod-like
#	- get_names(self) -> list											@staticmethod-like
#	- is_exists(self) -> bool											@staticmethod-like
#	- get_id_by_openweather_id(self, openweather_id: int) -> int		@staticmethod-like
#	- get_country(self, country_code: str) -> str						@staticmethod-like
#	- get_countries(self) -> dict										@staticmethod-like
#	- get_timezone(self, city_id: int) -> int							@staticmethod-like
#	- insert_timezone_if_not_exists(self, city) -> bool					@staticmethod-like
#	- get_openweather_id(self, city_name: str) -> int					staticmethod-like
#	- update_openweather_id(self, city_id: int, openweather_id: int)	@staticmethod-like
#############################################################################################################

from City import CityCRUD, CityNotFoundError
from GlobalServiceOptions import GlobalServiceOptions
from LogMe import info_message, error_message, frame_info, print_frame_info

class CityMySQL(CityCRUD):
	
	def __init__(self):
		'''CityMySQL constructor.'''

		self.options = GlobalServiceOptions()
		super().__init__(self.options)

	def load_tuple(self, item):
		'''Helper function that wraps the operation steps of loading from 
		a database table to a class object. Make assignments from the 
		list object 'item' to the 'self' object.'''

		try:
			self.id = int(item[0])
			self.city.name = item[1]
			self.city.longitude = float(item[2])
			self.city.latitude = float(item[3])
			self.city.country_code = item[4]
			self.city.timezone = int(item[5])

			self.city.openweather_id = 0
			if item[6]:
				self.city.openweather_id = int(item[6])

			self.city.state = item[7]

		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))

		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'Tuple loaded.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'Tuple loaded.'))

	def copy(self, other):
		'''Copy other object to self object'''

		try:
			self.id = self.get_id_by_openweather_id(other.city.openweather_id)
			self.city.name = other.city.name
			self.city.longitude = other.city.longitude
			self.city.latitude = other.city.latitude
			self.city.country_code = other.city.country_code
			self.city.timezone = other.city.timezone
			self.city.openweather_id = other.city.openweather_id
			self.city.state = other.city.state

		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
   
		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'Other copied.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'Other copied.'))

	def select(self):
		
		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT id, name, longitude, latitude, country_code, timezone, openweather_id, state FROM city WHERE id = %s"
			cur.execute(sql, (self.id, ))
			row = cur.fetchone()
			
			if row:
				self.load_tuple(row)

		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))

		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'City selected.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City selected.'))
		
		finally:
			if conn:
				conn.close()

	def get_all(self) -> list:
		
		cities = []

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT id, name, longitude, latitude, country_code, timezone, openweather_id, state FROM city"
			cur.execute(sql)
			rows = cur.fetchall()
			
			if rows:
				for row in rows:
					city = CityMySQL()
					city.load_tuple(row)
					cities.append(city)

			fi = frame_info()
			print(info_message(print_frame_info(fi), 'All cities selected.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'All cities selected.'))

			return cities
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
		
		finally:
			if conn:
				conn.close()

	def select_id(self):

		try:
			if self.city.name in self.options.config.city_names_json_db_diff.keys():
				self.city.name = self.options.config.city_names_json_db_diff[self.city.name]

			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT id FROM city WHERE name = %s"
			cur.execute(sql, (self.city.name, ))
			row = cur.fetchone()

			self.id = int(row[0])
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
		
		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'City id is got.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City id is got.'))
  
		finally:
			if conn:
				conn.close()

	def insert(self):
		# inserts into MySQL database
		conn = None

		try:
			
			if not self.is_exists(self):

				conn = self.options.db_Conn.createMySQLConnection()
				cur = conn.cursor()
				sql = 'INSERT INTO City(name, longitude, latitude, country_code, timezone, openweather_id, state) VALUES(%s, %s, %s, %s, %s, %s, %s)'

				cur.execute(sql, (self.city.name, self.city.longitude, self.city.latitude, self.city.country_code, self.city.timezone, self.city.openweather_id, self.city.state))

				cur.close()
				conn.commit()
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
   
		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'City inserted.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City inserted.'))
		
		finally:
			if conn:
				conn.close()

	def update(self):

		conn = None
		try:
			
			if not self.is_exists(self):

				conn = self.options.db_Conn.createMySQLConnection()
				cur = conn.cursor()

				sql = ''' UPDATE City SET name = %s, longitude = %s, latitude = %s, country_code = %s, timezone = %s, 
							openweather_id = %s, state = %s WHERE id = %s; '''

				cur.execute(sql, (self.city.name, self.city.longitude, self.city.latitude, self.city.country_code, self.city.timezone, self.openweather_id, self.city.state, self.id))

				cur.close()
				conn.commit()
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
   
		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'City updated.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City updated.'))
		
		finally:
			if conn:
				conn.close()

	def delete(self):
		
		conn = None
		try:
			
			if not self.is_exists(self):

				conn = self.options.db_Conn.createMySQLConnection()
				cur = conn.cursor()
				sql = ''' DELETE FROM city WHERE id = %s; '''

				cur.execute(sql, (self.id, ))

				cur.close()
				conn.commit()
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
   
		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'City deleted.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City deleted.'))
		
		finally:
			if conn:
				conn.close()

	def is_exists(self) -> bool:

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = 'SELECT COUNT(id) FROM city WHERE openweather_id = %s'
			cur.execute(sql, (self.city.openweather_id, ))
			row = cur.fetchone()

			fi = frame_info()
			print(info_message(print_frame_info(fi), 'City is exists checked.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City is exists checked.'))
   
			return int(row[0]) > 0
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
   
		finally:
			if conn:
				conn.close()

	def get_name(self, city_id: int) -> str:

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT name FROM city WHERE id = %s"
			cur.execute(sql, (city_id, ))
			row = cur.fetchone()

			fi = frame_info()
			print(info_message(print_frame_info(fi), 'City name is got.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City name is got.'))

			return str(row[0])
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
		
		finally:
			if conn:
				conn.close()
		
	def get_names(self) -> list:
		
		cities = []
		try:
			conn = self.options.db_Conn.createMySQLConnection()
			curr = conn.cursor()

			sql = "SELECT name FROM city"
			curr.execute(sql)

			rows = curr.fetchall()

			if rows:
				for row in rows:
					cities.append(row[0])

			curr.close()
			conn.commit()
   
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'All city names are got.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'All city names are got.'))

			return cities
		
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
			
		finally:
			if conn:
				conn.close()

	def get_id_by_openweather_id(self, openweather_id: int) -> int:

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT id FROM city WHERE openweather_id = %s"
			cur.execute(sql, (openweather_id, ))
			row = cur.fetchone()

			fi = frame_info()
			print(info_message(print_frame_info(fi), 'City id is got by openweather id.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City id is got by openweather id.'))

			return str(row[0])

		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))

		finally:
			if conn:
				conn.close()

	def get_country(self, country_code: str) -> str:
		# Returns the name of country queried by its country code as str

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT country FROM country_code WHERE alpha2_code = ?"
			cur.execute(sql, (country_code, ))
			row = cur.fetchone()
   
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'Country name is got by country code.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'Country name is got by country code.'))
   
			if row:
				return str(row[0])
				
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
		
		finally:
			if conn:
				conn.close()

	def get_countries(self) -> dict:
		# Returns all countries and their associated country codes in a dict
		countryDict = {}

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT country, alpha2_code FROM country_code"
			cur.execute(sql)
			rows = cur.fetchall()
			if rows:
				for row in rows:
					countryDict[row[1]] = row[0]
					
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'All countries are got into a dictionary.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'All countries are got into a dictionary.'))
     
			return countryDict
				
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
		
		finally:
			if conn:
				conn.close()

	def get_timezone(self, city_id: int) -> int:
		# Returns timezone of city in integer format
		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT timezone FROM city WHERE id = %s"
			cur.execute(sql, (city_id, ))
			row = cur.fetchone()
			cur.close()

			if row:
				fi = frame_info()
				print(info_message(print_frame_info(fi), 'City timezone is got.'))
				self.options.logMe.logs.append(info_message(print_frame_info(fi), 'City timezone is got.'))
       
				timezone = int(row[0])
				timezone = timezone / 3600
				return int(timezone)

			raise Exception('CitySQLite.get_timezone(city_id) -> int => Can\'t get timezone')
				
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
		
		finally:
			if conn:
				conn.close()

	def insert_timezone_if_not_exists(self, city) -> bool:

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT COUNT(timezone) FROM city WHERE openweather_id = %s"
			cur.execute(sql, (city.city.openweather_id, ))
			row = cur.fetchone()

			if row:
				exists = (int(row[0]) > 0)

				if not exists:
					sql = "UPDATE City SET timezone = %s WHERE id = %s"
					cur.execute(sql, (city.timezone, city.openweather_id))

					conn.commit()
					cur.close()
				
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
   
		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'Timezone is inserted if not existed before.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'Timezone is inserted if not existed before.'))
      
		finally:
			if conn:
				conn.close()

	def get_openweather_id(self, city_name: str) -> int:

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = "SELECT openweather_id FROM city WHERE name = %s"
			cur.execute(sql, (city_name, ))
			row = cur.fetchone()

			fi = frame_info()
			print(info_message(print_frame_info(fi), 'openweather id is got.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'openweather id is got.'))

			return int(row[0])
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
		
		finally:
			if conn:
				conn.close()

	def update_openweather_id(self, city_id: int, openweather_id: int):

		try:
			conn = self.options.db_Conn.createMySQLConnection()
			cur = conn.cursor()

			sql = 'UPDATE City SET openweather_id = %s WHERE id = %s'

			cur.execute(sql, (openweather_id, city_id))

			cur.close()
			conn.commit()
			
		except Exception as error:
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.options.logMe.logs.append(error_message(print_frame_info(fi), error))
		
		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'openweather id is updated.'))
			self.options.logMe.logs.append(info_message(print_frame_info(fi), 'openweather id is updated.'))
  
		finally:
			if conn:
				conn.close()
