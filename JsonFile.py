import os
import json
import ijson
from datetime import datetime

from ConfigParserWrapper import ConfigParserWrapper
from OpenWeatherException import CityNotFoundError
from LogMe import LogMe, info_message, error_message, frame_info, print_frame_info

# class JsonFile:

# 	def __init__(self, json_file_path = None):

# 		self.data = None
# 		self.datarows = None

# 		self.logMe = LogMe()
		
# 		self.config_wrapper = ConfigParserWrapper()
# 		self.config_wrapper.read('serviceconfig.ini')

# 		if json_file_path:
# 			self.json_file_path = json_file_path
# 		else:
# 			self.json_file_path = self.config_wrapper.get('OpenWeather.Resources.Json', 'CityList')

# 		self.data_directory = self.config_wrapper.get('Directories', 'DataDirectory')

# 	def load_data(self):

# 		try:
# 			if not self.json_file_path:
# 				self.logMe.write(error_message('JsonFile::load_data() -> json_file_path not found', Exception()))
# 				raise Exception(error_message('JsonFile::load_data()', Exception()))
				
# 			f = open(self.json_file_path, "r", encoding="utf-8")
# 			self.data = json.loads(f.read())
# 			f.close()

# 		except Exception as error:
# 			fi = frame_info()
# 			print(error_message(print_frame_info(fi), error))
# 			self.logMe.write(error_message(print_frame_info(fi), error))
# 		else:
# 			print(info_message('JsonFile::load_data()', 'JsonFile loaded.'))
# 			self.logMe.write(info_message('JsonFile::load_data()', 'JsonFile loaded.'))
			

# 	def save_data(self, data_dict):

# 		# Serializing json
# 		json_object = json.dumps(data_dict, indent=4)

# 		self.filename = f'{datetime.now().strftime("%Y.%m.%d-%H%M%S")}_openweather.json'	# %Y.%m.%d %H%M%S
# 		raw_data_filename = os.path.join(self.raw_data_directory, self.filename) 

# 		try:
# 			f = None
# 			if os.path.exists(raw_data_filename):
# 				f = open(raw_data_filename, "a")
# 			else:
# 				f = open(raw_data_filename, "w")

# 			f.write(json_object)

# 		except Exception as error:
# 			fi = frame_info()
# 			print(error_message(print_frame_info(fi), error))
# 			self.logMe.write(error_message(print_frame_info(fi), error))

# 		else:
# 			print(info_message('JsonFile::save_data()', 'JsonFile saved.'))
# 			self.logMe.write(info_message('JsonFile::save_data()', 'JsonFile saved.'))


# 	def get_openweather_id(self, city_name) -> int:

# 		if not self.data:
# 			self.data = self.load_data()

# 		try:
# 			for item in self.data:
# 				if item["name"] == city_name:
# 					return int(item["id"])

# 		except Exception as error:
# 			fi = frame_info()
# 			print(error_message(print_frame_info(fi), error))
# 			self.logMe.write(error_message(print_frame_info(fi), error))

# 		else:
# 			print(info_message('JsonFile::get_openweather_id()', 'id is ok.'))
# 			self.logMe.write(info_message('JsonFile::get_openweather_id()', 'id is ok.'))

# 		raise CityNotFoundError(f'JsonFile::get_city_id() cannot find {city_name} in city.list.json file.')

# 	def get_cities_homonymous(self, city_name) -> list:

# 		# searches the city_name in city.list.json file.
# 		# city.list.json file contains more than one city
# 		# with the same name. This method builds a City 
# 		# object for each city with the same name and 
# 		# returns them as a list object.
# 		# NOTE: # This object will not contain
# 		# timezone data because city.list.json file doesn't
# 		# contain timezone data. This data must be obtained
# 		# via WeatherData.timezone variable after web query. 
# 		# if city cannot be found in city.list.json returns None.

# 		# Returns a list of cities. 
# 		# There could be more than one city with the same name.
# 		# To find the right city, check their country code, lon, lat info. 

# 		cities = []

# 		if not self.data:
# 			self.load_data()

# 		try:
# 			for item in self.data:
# 				if item["name"] == city_name:
# 					city = City()
# 					city.name = city_name
# 					city.openweather_id = int(item["id"])
# 					city.state = item["state"]
# 					city.country_code = item["country"]
# 					city.longitude = item["coord"]["lon"]
# 					city.latitude = item["coord"]["lat"]
# 					cities.append(city)

# 		except Exception as error:
# 			fi = frame_info()
# 			print(error_message(print_frame_info(fi), error))
# 			self.logMe.write(error_message(print_frame_info(fi), error))
# 			return None
		
# 		else:
# 			print(info_message('JsonFile::get_cities_homonymous()', 'City is loaded.'))
# 			self.logMe.write(info_message('JsonFile::get_cities_homonymous()', 'City is loaded.'))

# 		return cities

# 	def get_all_cities(self, callback=None) -> list:

# 		if not self.data:
# 			self.load_data()

# 		cities = []

# 		try:
# 			for item in self.data:
# 				city = City()
# 				city.openweather_id = int(item["id"])
# 				city.name = item["name"]
# 				city.state = item["state"]
# 				city.country_code = item["country"]
# 				city.longitude = item["coord"]["lon"]
# 				city.latitude = item["coord"]["lat"]
# 				if callback:
# 					callback(city)
# 				else:
# 					cities.append(city)

# 		except Exception as error:
# 			fi = frame_info()
# 			print(error_message(print_frame_info(fi), error))
# 			self.logMe.write(error_message(print_frame_info(fi), error))
# 			return None
		
# 		else:
# 			print(info_message('JsonFile::get_all_cities()', 'Cities are loaded.'))
# 			self.logMe.write(info_message('JsonFile::get_all_cities()', 'Cities are loaded.'))

# 		# if a callback method passed as an argument, 
# 		# return value is unnecessary
# 		if callback:
# 			return None

# 		return cities

# 	def get_all_data(self) -> list:

# 		self.get_all_cities(self.add_row_to_data_rows)

# 	def add_row_to_data_rows(self, city):

# 		if not self.datarows:
# 			self.datarows = []

# 		self.datarows.append([city.name, city.longitude, city.latitude, city.country_code, city.timezone, city.openweather_id, city.state])

class IJsonFile:

	@staticmethod
	def traverse(callback, path, *args):

		with open(path, 'r', encoding='utf-8') as f:

			# Parse the JSON objects one by one
			parser = ijson.items(f, 'item')
			
			# Iterate over the JSON objects
			for item in parser:
				# Process each JSON object as needed
				callback(item, *args)
	