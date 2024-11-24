from datetime import datetime
from ConfigParserWrapper import ConfigParserWrapper
import requests

class OpenWeatherData:

	def __init__(self, json=None, url=None, query_time=None):

		self.json = json
		self.url = url
		self.query_time = query_time

class OpenWeatherServer:

	def __init__(self, api_key):
		
		config_wrapper = ConfigParserWrapper()
		self.base_url = config_wrapper.get('OpenWeather.Server', 'Url')

	def get_response(self, city_name, units='metric'):

		url = self.prepare_query_url(city_name)
		response = requests.get(url)

		return (response, url)

	# standard, metric and imperial units are available. 
	# If you do not use the units parameter, standard units 
	# will be applied by default.
	def get_single_openweatherdata(self, city_name, units='metric') -> OpenWeatherData:

		response, url = self.get_response(city_name, units)
		query_time = datetime.now()

		return OpenWeatherData(response.json(), url, query_time)
	
	def get_group_openweatherdata(self, id_list, units='metric') -> OpenWeatherData:

		url = self.prepare_group_query_url(id_list)
		response = requests.get(url)
		query_time = datetime.now()

		return OpenWeatherData(response.json(), url, query_time)

	def get_responses(self, id_list, units='metric'):

		url = self.prepare_group_query_url(id_list)
		response = requests.get(url)
		query_time = datetime.now()
		
		return (response, url, query_time)

	def prepare_group_query_url(self, id_list):
		
		# https://api.openweathermap.org/data/2.5/group?id=745044,745028&appid=2c75cebf6d3e393d366492f96cf33132

		query_token = str(id_list)
	
		return f'https://api.openweathermap.org/data/2.5/group?id={query_token}&appid={self.api_key}'

	def prepare_query_url(self, city_name, units='metric'):
	
		return f'{self.base_url}appid={self.api_key}&q={city_name}&units={units}'