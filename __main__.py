'''	module info
# Filename: openweather41
# Extension: pyw
# Version: 0.04.1
# Project: OpenWeather
# Description: Project's main file
# Creator: Berk Acunaş
# Created on: 2023.05.04
'''

from datetime import datetime
from configparser import ConfigParser
import math
import argparse

from OpenWeatherServer import OpenWeatherServer
from OpenWeatherLogger import OpenWeatherLogger
from OpenWeatherException import ApiKeyNotFoundError
from WeatherData import WeatherData
from WeatherDataParser import WeatherDataParser
from City import City
from MySQLConnection import DBConnection
from LogMe import LogMe, info_message, error_message
from Initializer import Initializer

# Global variables
initilizer = Initializer()
config = ConfigParser()
config.read('serviceconfig.ini')


def exists(var):
	return var in globals() or var in locals()

def do_you_want_to_continue(message: str) -> bool:

	message += ' (Y/n)'
	print(message, end=' ')
	response = input()
	return str.lower(response) == 'y'

def global_parser_func(args):

	if args.daemon:
		initilizer.add_cron_job()

def subparser_apikey_func(args):

	if args.newvalue:

		message = 'Your new api key will overwrite previous api key. There will be no return.'
		if do_you_want_to_continue(message):
			api_key = args.newvalue
			initilizer.save_api_key(api_key)

	if args.print:
		try:
			api_key = initilizer.load_api_key()
			print(f'Api Key: {api_key}')

		except ApiKeyNotFoundError as error:
			print('Api Key not found !')
		
def subparser_db_func(args):

	if args.create:

		message = 'Do you want to create a MySQL database? If database already exists, this step will have no effect.'
		if do_you_want_to_continue(message):
			print('Enter your database username: ', end=' ')
			db_username = input()
			print('When it asks for password, it\'s your database login password. OpenWeather doesn\'t store this password for security reasons.')
			DBConnection().executeSqlFile(db_username)

	if args.activate:

		message = 'Do you want to activate MySQL database?'
		if do_you_want_to_continue(message):
			config.set('Database.Online', 'activated', 'True')
			with open('serviceconfig.ini', "w") as f:
				config.write(f)
	
	if args.deactivate:

		message = 'Do you want to deactivate MySQL database?'
		if do_you_want_to_continue(message):
			config.set('Database.Online', 'activated', 'False')
			with open('serviceconfig.ini', "w") as f:
				config.write(f)

def main():
	
	start_time = datetime.now()
	print(f'Started at {start_time}')

	cities = None
	logMe = LogMe()

	try:
		i = 0
		k = 0
		index = 0
		api_key = None
		
		global_parser = argparse.ArgumentParser(prog='openweather', 
								   		 description='OpenWeather Server and Data Management Module',
										 epilog='Thanks for using %(prog)s!')
		
		global_parser.add_argument('-d', '--daemon', action="store_true", help='Run as daemon')
		global_parser.set_defaults(func=global_parser_func)
		

		subparsers = global_parser.add_subparsers(title="subcommands")

		api_parser = subparsers.add_parser('apikey', help='Api Key Operations')
		api_parser.add_argument('-n', '--newvalue', help='Enter new value')
		api_parser.add_argument('-p', '--print', action='store_true', help='Print Api Key to stdout')
		api_parser.set_defaults(func=subparser_apikey_func)


		db_parser = subparsers.add_parser('db', help='Database Operations')
		db_parser.add_argument('-c', '--create', action='store_true')
		db_parser.add_argument('-a', '--activate', action='store_true')
		db_parser.add_argument('-d', '--deactivate', action='store_true')

		db_parser.set_defaults(func=subparser_db_func)

		args = global_parser.parse_args()

		try:
			if args.func:
				args.func(args)
		except AttributeError as error:
			pass
		
		try :
			api_key = initilizer.load_api_key()
		except ApiKeyNotFoundError as apikeyerror:
			print('Api Key not found! Please register your Api Key.\ne.g. $ openweather api --newkey yourapikey')
			return
			
		ows = OpenWeatherServer(api_key)

	

		if True:
			return
		
		

		city = City()
		openweather_ids = city.get_all_openweather_ids()

		max_query_limit = config.getint('Settings', 'MaxGroupQueryLimit')
		loop_count = math.ceil(len(openweather_ids) /  max_query_limit)
		
		rows = []
		query_ids = []
		query_token = ''

		for i in range(loop_count):
			
			for k in range(max_query_limit):

				if index == len(openweather_ids):
					break

				query_ids.append(str(openweather_ids[index]))
				index += 1
			
			if len(query_ids) > 0:
				query_token = ''
				query_token = ','.join(query_ids)[:-1]

				openweatherdata = ows.get_group_openweatherdata(query_token)
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



if __name__ == "__main__":
	main()