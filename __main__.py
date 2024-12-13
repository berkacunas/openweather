'''	module info
# Filename: openweather43
# Extension: py
# Version: 0.4.3
# Project: OpenWeather
# Description: Project's main file
# Creator: Berk Acunaş
# Created on: 2023.05.04
'''
import os
import sys
from datetime import datetime
import math
import argparse

from Initializer import Initializer
from ConfigParserWrapper import ConfigParserWrapper
from OpenWeatherClient import OpenWeatherClient
from OpenWeatherLogger import OpenWeatherLogger
from OpenWeatherException import ApiKeyNotFoundError
from WeatherData import WeatherData
from WeatherDataParser import WeatherDataParser
from City import City, CityJson, UserCityJson
from CountryCode import CountryCode
from MySQLConnection import DbOptions
from LogMe import LogMe, info_message, error_message

# Global variables, definitions
logMe = LogMe()

cwd = os.getcwd()
init_dir = os.path.join(cwd, '.init')

initializer = Initializer(cwd)
config_wrapper = ConfigParserWrapper()
	
if initializer.inited:
	db_options = DbOptions()

def _extract_city_data(args):
	
	count = len(args)

	city_name = args[0]
	state = None
	country_code = None

	if count == 3:
		state = args[1]
		country_code = args[2]
	if count == 2:
		country_code = args[1]
  
	return city_name, state, country_code

def _do_you_want_to_continue(message: str) -> bool:

	message += ' (Y/n)'
	print(message, end=' ')
	response = input()
	return str.lower(response) == 'y'

def global_parser_func(args):

	if args.daemon:
		initializer.add_cron_job()

def subparser_init_parser_func(args):
	
	init_dir = os.path.join(cwd, '.init')

	if os.path.exists(init_dir):
		print('OpenWeather has already initialized before.')
		return
	
	initializer.init(cwd)

def subparser_status_parser_func(args):

	raise NotImplementedError('Not implemented yet !')

def subparser_apikey_func(args):

	if args.newvalue:

		message = 'Your new api key will be overwritten your previous api key. There will be no return.'
		if _do_you_want_to_continue(message):
			api_key = args.newvalue
			initializer.save_api_key(api_key)

	if args.print:
		try:
			api_key = initializer.load_api_key()
			print(f'Api Key: {api_key}')

		except ApiKeyNotFoundError as error:
			raise
		
def subparser_db_func(args):

	if args.set_credentials:

		print('Enter your host name: ', end=' ')
		host = input()
		print('Enter your database name: ', end=' ')
		database = input()
		print('Enter your username: ', end=' ')
		username = input()
		print('Enter your password: ', end=' ')
		password = input()
		print('Enter port: (Hit enter for default port: 3306)', end= ' ')
		port = input()
		if port == '':
			port = 3306

		db_options.createUser(host, database, username, password, port)

	if args.create:

		message = 'Do you want to create a MySQL database? If database already exists, this step will have no effect.'
		if _do_you_want_to_continue(message):

			print('When it asks for password, please enter your database user password.')
			db_options.executeSqlFile()

	if args.enable:

		message = 'Do you want to enable MySQL database?'
		if _do_you_want_to_continue(message):
			db_options.enableDatabase(True)
	
	if args.disable:

		message = 'Do you want to disable MySQL database?'
		if _do_you_want_to_continue(message):
			db_options.enableDatabase(False)


def subparser_city_func(args):

	if args.search:

		city_name, state, country_code = _extract_city_data(args.search)
		CityJson.find(city_name, state, country_code)
		
		for match in CityJson.search_matches:
			print(match)

	if args.openweather_id:

		city_name, state, country_code = _extract_city_data(args.openweather_id)
		CityJson.find_openweather_id(city_name, state, country_code)

	if args.add:

		openweather_id = int(args.add[0])
		CityJson.find_by_openweather_id(openweather_id)
		
		user_city = UserCityJson()
		if not str(openweather_id) in user_city.data:
			user_city.data[openweather_id] = dict(CityJson.search_matches[0])
			user_city.save()

	if args.remove:
		openweather_id = int(args.remove[0])

		user_city = UserCityJson()
		if str(openweather_id) in user_city.data:
			user_city.data.pop(str(openweather_id))
			user_city.save()

	if args.list:
		user_city = UserCityJson()
		print(user_city)


	if args.last_weather:

		city_name, state, country_code = _extract_city_data(args.last_weather)
		weatherData = City.get_last_weather(city_name, state, country_code)
		print(weatherData)

def subparser_country_func(args):


	if args.search_code:

		country_name = CountryCode.get_country_code(args.search_code[0])
		print(country_name)


	if args.search_name:
		
		country_code = CountryCode.get_country_name(args.search_name[0])
		print(country_code)


def subparser_query_func(args):

	api_key = None
 
	try :
		api_key = initializer.load_api_key()
		owc = OpenWeatherClient(api_key)
  
	except ApiKeyNotFoundError as apikeyerror:
		print('Api Key not found! Please register your Api Key.\ne.g. $ openweather apikey --newvalue yourapikey')
		return
 
	if args.city:

		city_name, state, country_code = _extract_city_data(args.city)
  
		try:
			data = owc.get_single_openweatherdata(city_name, state, country_code).json
			parser = WeatherDataParser()
			weatherData = parser.parse(data)
			print(weatherData)

		except Exception as error:
			print('Cannot get current weather data.')

	if args.query_all:
	 
		try:
			i = 0
			k = 0
			index = 0

			start_time = datetime.now()
			print(f'Started at {start_time}')
			
			city = City()	
			openweather_ids = city.get_all_openweather_ids()

			max_query_limit = config_wrapper.getint('Settings', 'MaxGroupQueryLimit')
			loop_count = math.ceil(len(openweather_ids) /  max_query_limit)
			
			rows = []
			query_ids = []
			query_token = ''

			for i in range(loop_count):
				
				for k in range(max_query_limit):

					if (index) == len(openweather_ids):
						break

					print(f'{index}: {openweather_ids[index]}')
					query_ids.append(str(openweather_ids[index]))
					index += 1
				
				if len(query_ids) > 0:
					query_token = ''
					query_token = ','.join(query_ids)[:-1]

					openweatherdata = owc.get_group_openweatherdata(query_token)
					datalist = openweatherdata.json

					first_data_dt = int(datalist['list'][0]["dt"])

					logger = OpenWeatherLogger()
					logger.mark(first_data_dt, openweatherdata.url, openweatherdata.query_time)
					logger_id = logger.add()				

					for data in datalist['list']:
						try:
							parser = WeatherDataParser()
							weatherData = parser.parse(data, is_kelvin_to_celcius=True)
							weatherData.logger_id = logger_id

							if not weatherData.is_exists():
								if not weatherData.city_id or weatherData.city_id == -1:
									print(error_message('main()::under \'for data in datalist[\'list\']:\'', f'Cannot download data of city openweather id: {openweather_ids[index]}. Skipped.'))
									logMe.write(error_message('main()::under \'for data in datalist[\'list\']:\'', f'Cannot download data of city openweather id: {openweather_ids[index]}. Skipped.'))
								else:
									rows.append(weatherData.to_list())

						except Exception as error:
							print(error_message('main()::under \'for data in datalist[\'list\']:\'', error))
							logMe.write(error_message('main()::under \'for data in datalist[\'list\']:\'', error))

					query_ids.clear()
					k = 0

			try:
				if len(rows) > 0:
					weatherData.add_all(rows)

					print(info_message('main()', f'{len(rows)} records successfull added to database.'))
					logMe.write(info_message('main()', f'{len(rows)} records successfull added to database.'))

			except Exception as mysql_error:
				print(error_message('main()::under \'weatherData.add_all(rows)\'', error))
				logMe.write(error_message('main()::under \'weatherData.add_all(rows)\'', error))

			end_time = datetime.now()

			service_uptime = end_time - start_time
			service_complete_log = f'Queries completed successfully in {service_uptime}'

			print(info_message('main()', service_complete_log))
			logMe.write(info_message('main()', service_complete_log))

		except Exception as error:
			print(error_message('main():: main block error', error))
			logMe.write(error_message('main():: main block error', error))



def main():

	global_parser = argparse.ArgumentParser(prog='openweather', 
											description='OpenWeather Server and Data Management Module',
										 epilog='Thanks for using %(prog)s!')
		
	global_parser.add_argument('-d', '--daemon', action="store_true", help='Run as daemon')
	global_parser.set_defaults(func=global_parser_func)

	subparsers = global_parser.add_subparsers(title="subcommands")

	init_parser = subparsers.add_parser('init', help='First Run Initialize Operations')
	init_parser.set_defaults(func=subparser_init_parser_func)

	status_parser = subparsers.add_parser('status')
	status_parser.set_defaults(func=subparser_status_parser_func)

	api_parser = subparsers.add_parser('apikey', help='Api Key Operations')
	api_parser.add_argument('-n', '--newvalue', help='Enter new value')
	api_parser.add_argument('-p', '--print', action='store_true', help='Print Api Key to stdout')
	api_parser.set_defaults(func=subparser_apikey_func)

	db_parser = subparsers.add_parser('db', help='Database Operations')
	db_parser.add_argument('-c', '--create', action='store_true')
	db_parser.add_argument('-e', '--enable', action='store_true')
	db_parser.add_argument('-d', '--disable', action='store_true')
	db_parser.add_argument('-s', '--set-credentials', action='store_true')
	db_parser.set_defaults(func=subparser_db_func)

	city_parser = subparsers.add_parser('city', help='City Operations')
	city_parser.add_argument('-s', '--search', nargs='+', action='store', help='"cityname" optional:"state" "countrycode"')
	city_parser.add_argument('-o', '--openweather-id', nargs=2, action='store', help='Print OpenWeather id of selected city')
	city_parser.add_argument('-a', '--add', nargs=1, action='store', help='Add city by its openweather id')
	city_parser.add_argument('-r', '--remove', nargs=1, action='store', help='Remove city by its openweather id')
	city_parser.add_argument('-l', '--list', action='store_true', help='List cities')
	city_parser.add_argument('-w', '--last-weather', nargs=2, action='store', help='Print last fetched observation data from database')
	city_parser.set_defaults(func=subparser_city_func)

	country_parser = subparsers.add_parser('country', help='Country Operations')
	country_parser.add_argument('-c', '--search-code', nargs=1, action='store', help='Enter country name')
	country_parser.add_argument('-n', '--search-name', nargs=1, action='store', help='Enter country name')
	country_parser.set_defaults(func=subparser_country_func)

	query_parser = subparsers.add_parser('query', help='Server Queries')
	query_parser.add_argument('-a', '--query-all', action='store_true', help='Fetch all last data from all cities from server')
	query_parser.add_argument('-c', '--city', nargs='+', action='store', help='Fetch current data from server for selected city')
	query_parser.set_defaults(func=subparser_query_func)

	try:
		args = global_parser.parse_args()

		if args.func:
			args.func(args)
		
		arg_len = len(sys.argv)
		if arg_len > 1:
			return

	except AttributeError as attributeError:
		print(error_message('main()::args.func(args)', attributeError))
		logMe.write(error_message('main()::args.func(args)', attributeError))
		pass

	except ApiKeyNotFoundError as apiKeyNotFoundError:
		print(error_message('main()::args.func(args)', apiKeyNotFoundError))
		logMe.write(error_message('main()::args.func(args)', apiKeyNotFoundError))
		return
	
	except Exception as error:
		print(error_message('main()::args.func(args)', error))
		logMe.write(error_message('main()::args.func(args)', error))
		return
	

if __name__ == "__main__":
	main()

