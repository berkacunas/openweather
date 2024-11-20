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
from LogMe import LogMe, info_message, error_message
from Initializer import Initializer

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

		initilizer = Initializer()
		
		try :
			api_key = initilizer.load_api_key()
		except ApiKeyNotFoundError as apikeyerror:
			print('Please register your OpenWeather API KEY: ')
			api_key = input()
			initilizer.save_api_key(api_key)

		ows = OpenWeatherServer(api_key)

		config = ConfigParser()
		config.read('serviceconfig.ini')

		parser = argparse.ArgumentParser(prog="openweather")

		'''
		İLK ÇALIŞTIRMA
		1. User'a kendi API key'ini sorsun. (API_KEY bir dosyada tek yönlü kullanıcı şifresi ile şifrelenmiş tutulsun.)
		2. MySQL veritabanı kurmasının istenip istenilmediği sorulsun.
		3. Çıktıyı komut satırına (stdout), txt veyas json dosyasına isteyip istemediği sorulsun.
		
		ÇALIŞ
		1. Şehrin o anki weatherdata bilgilerini indirip stdout'a yazsın.
		2. Günlük kaç server query atıldığı hakkında datetime'ları ile bir flag ya da subcommand ile ile bilgilendirilsin. ex. openweather log gibi
		3. Komut satırından argüman olarak girilen şehirlerin openweather_id'leri döndürülsün.
		4. openweather_id ile group query atılsın.
		5. Veritabanı yaratılmışsa herhangi bir şehrin istenen datetime bilgilerindeki WeatherData'sı döndürülsün.
		'''
		
		# parser.add_argument("path")

		args = parser.parse_args()
		path = args.path

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