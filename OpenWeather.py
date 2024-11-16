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

from OpenWeatherServer import OpenWeatherServer
from OpenWeatherLogger import OpenWeatherLogger
from WeatherData import WeatherData
from City import City
from LogMe import error_message
from Initializer import Initializer

def main():

	start_time = datetime.now()
	print(f'Started at {start_time}')

	cities = None
	
	try:

		i = 0
		k = 0
		index = 0

		initilizer = Initializer()
		ows = OpenWeatherServer()
		# jsonFile = JsonFile(options)
		
		config = ConfigParser()
		config.read('serviceconfig.ini')

		
		city = City()
		################################################################ 1

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
						weatherDataMySQL = WeatherDataMySQL(options)
						weatherDataMySQL.wd.parse(data, kelvin_to_celcius=True)
						weatherDataMySQL.query_id = loggerMySQL_id

						if not weatherDataMySQL.is_dt_exists():
							rows_mysql.append(weatherDataMySQL.to_list())

					except Exception as error:
						print(error_message('main() => weatherDataMySQL.parse(data, kelvin_to_celcius=True)', error))
						log_list.append(error_message('main() => weatherDataMySQL.parse(data, kelvin_to_celcius=True)', error))

				openweather_id_list.clear()
				k = 0

		try:
			if len(rows_mysql) > 0:
				weatherDataMySQL.insertmany(rows_mysql)

				mysql_log = f'New MySQL Records          --->    {len(rows_mysql)}'
				print(mysql_log)
				log_list.append(mysql_log)

		except Exception as mysql_error:
			print(f'Error at weatherDataMySQL.insertmany(rows) -> int : {mysql_error}')
			

		end_time = datetime.now()

		query_duration = end_time - start_time
		query_log = f'Query completed successfully in {query_duration} '
		print(query_log)
		log_list.append(query_log)

	except Exception as error:
		print(error_message('main()', error))
		# log_list.append(error_message('main()', error))
		pass
	
	finally:
		pass
		# if options.config.log_on:
		# 	log_list_to_file(options)


if __name__ == "__main__":
	main()