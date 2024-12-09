from ConfigParserWrapper import ConfigParserWrapper
import json

from datetime import datetime
from WeatherData import WeatherData
from City import City
from LogMe import LogMe, info_message, error_message
from OpenWeatherException import CityNotFoundError, ServerDataIsEmptyError

class WeatherDataParser:

	def __init__(self):

		self.config_wrapper = ConfigParserWrapper()
		self.logMe = LogMe()

		city_conflicts_file = self.config_wrapper.get('Data', 'CityConflictsJsonFile')

		with open(city_conflicts_file) as f:
			self.city_conflicts = json.load(f)

	def parse(self, data=None, is_kelvin_to_celcius=False) -> WeatherData:

		weatherData = None

		if not data:
			raise ServerDataIsEmptyError()

		try:

			weatherData = WeatherData()

			# # Now data contains list of nested dictionaries. Check the value of "cod" key is equal to
			# # "404", means city is found other.wise, city is not found
			# if data["cod"] != "404":
			
			weatherData.date = datetime.now().strftime('%Y.%m.%d')
			weatherData.time = datetime.now().strftime('%H:%M.%S')
			
			# store the value of "dictionary keys in their own variables.
			coord = data["coord"]
			weather = data["weather"]
			main = data["main"]
			wind = data["wind"]
			clouds = data["clouds"]
			sys = data["sys"]
			
			weatherData.visibility = data["visibility"]
			weatherData.dt = data["dt"]
			weatherData.sys = data["sys"]
			
			city_name = self.city_conflicts.get(data["name"])
			if not city_name:
				city_name = data["name"]

			weatherData.city_id = City().get_id_by_name(city_name, None, weatherData.sys['country'])
			if (weatherData.city_id == -1) or (weatherData.city_id == None):
				raise CityNotFoundError(error_message('WeatherDataParser.parse()', f'Cannot find city id of {city_name}'))
			
			weatherData.longitude = float(coord["lon"])
			weatherData.latitude = float(coord["lat"])
			weatherData.description = weather[0]["description"]
			weatherData.weather_type = weather[0]["main"]
			weatherData.icon = weather[0]["icon"]

			celcius_kelvin_diff = self.config_wrapper.getfloat('Units', 'KelvinToCelcius')

			if is_kelvin_to_celcius:
				weatherData.temperature = float(main["temp"]) - celcius_kelvin_diff
			else:
				weatherData.temperature = float(main["temp"])

			if is_kelvin_to_celcius:
				weatherData.feels_like = float(main["feels_like"]) - celcius_kelvin_diff
			else:
				weatherData.feels_like = float(main["feels_like"])
			
			weatherData.pressure = int(main["pressure"])
			weatherData.humidity = int(main["humidity"])

			if is_kelvin_to_celcius:
				weatherData.temperature_min = float(main["temp_min"]) - celcius_kelvin_diff
			else:
				weatherData.temperature_min = float(main["temp_min"])

			if is_kelvin_to_celcius:
				weatherData.temperature_max = float(main["temp_max"]) - celcius_kelvin_diff
			else:
				weatherData.temperature_max = float(main["temp_max"])

			weatherData.wind_speed = float(wind["speed"])
			weatherData.wind_degree = int(wind["deg"])
			weatherData.cloudiness = clouds["all"]
			weatherData.country_code = sys["country"]
			weatherData.sunrise = sys["sunrise"]
			weatherData.sunset = sys["sunset"]

			try:
				weatherData.timezone = int(sys["timezone"])
			except:
				weatherData.timezone = int(data["timezone"])

			weatherData.hour_of_the_day = datetime.fromtimestamp(weatherData.dt).hour

			print(info_message('WeatherDataParser::parse()', 'Raw data from OpenWeather server parsed into a WeatherData object.'))
			self.logMe.write(info_message('WeatherDataParser::parse()', 'Raw data from OpenWeather server parsed into a WeatherData object.'))

		except Exception as error:
			print(error_message('WeatherDataParser.parse()', error))
			self.logMe.write(error_message('WeatherDataParser.parse()', error))

		return weatherData
	