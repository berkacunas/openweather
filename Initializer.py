import os
from datetime import datetime
import dateutil.tz
from subprocess import run
from configparser import ConfigParser

from OpenWeatherException import ApiKeyNotFoundError, ApiKeyDuplicateError
import CryptoSymmetric
from LogMe import LogMe, error_message

class Initializer:

	def __init__(self, cwd):

		self.cwd = cwd
		self.init_dir = os.path.join(cwd, '.init')
		self.config_path = os.path.join(self.init_dir, 'config.ini')
		self.config = ConfigParser()

		if not os.path.exists(self.init_dir):
			return 
		
		self.logMe = LogMe()
		self.config = ConfigParser()

		self.config.read(self.config_path)
		
		self.do_init()

	def init(self, cwd):

		if os.path.exists(self.init_dir):
			return 
	
		os.mkdir(self.init_dir)
		
		if not os.path.isfile(self.config_path):
			with open(self.config_path, 'x') as f:
				f.close()

		self.config.read(self.config_path)

		self.config.add_section('Directories')
		self.config.add_section('Application')
		self.config.add_section('Paths')
		self.config.add_section('Flags')
		self.config.add_section('OpenWeather.Server')
		self.config.add_section('OpenWeather.Resources.Json')
		self.config.add_section('Database')
		self.config.add_section('Database.MySQL')
		self.config.add_section('Data')
		self.config.add_section('Settings')
		self.config.add_section('Units')
		self.config.set('Directories', 'RootDirectory', self.cwd)
		self.config.set('Directories', 'InitDirectory', self.init_dir)
		self.config.set('Directories', 'DataDirectory', os.path.join(self.cwd, 'data'))
		self.config.set('Directories', 'CsvDirectory', os.path.join(self.cwd, 'csv'))
		self.config.set('Directories', 'JsonDirectory', os.path.join(self.cwd, 'json'))
		self.config.set('Directories', 'LogDirectory', os.path.join(self.cwd, 'log'))
		self.config.set('Directories', 'BackupDirectory', os.path.join(self.cwd, 'backup'))
		self.config.set('Application', 'EntryPoint', '__main__.py')
		self.config.set('Paths', 'ApiKeyFile', os.path.join(self.cwd, 'data', 'api.key'))
		self.config.set('Paths', 'SecretKeyFile', os.path.join(self.cwd, 'data', 'secret.key'))
		self.config.set('Paths', 'DbSchemaFile', os.path.join(self.cwd, 'data', 'openweather-mysql-schema.sql'))
		self.config.set('Flags', 'JsonOn', 'False')
		self.config.set('Flags', 'CsvOn', 'False')
		self.config.set('Flags', 'LogOn', 'False')
		self.config.set('OpenWeather.Server', 'Url', 'https://api.openweathermap.org/data/2.5/weather?')
		self.config.set('OpenWeather.Resources.Json', 'CityList', os.path.join(self.cwd, 'resources', 'city.list.json'))
		self.config.set('OpenWeather.Resources.Json', 'CurrentCityList', os.path.join(self.cwd, 'resources', 'current.city.list.json'))
		self.config.set('Database', 'Activated', 'False')
		self.config.set('Database.MySQL', 'Host', 'localhost')
		self.config.set('Database.MySQL', 'DbName', 'OpenWeather')
		self.config.set('Database.MySQL', 'Username', 'barishuan')
		self.config.set('Database.MySQL', 'Password', 'xHV.H|3<P~')
		self.config.set('Data', 'CityConflictsJsonFile', os.path.join(self.cwd, 'data', 'CityNameConflicts.json'))
		self.config.set('Settings', 'MaxGroupQueryLimit', '20')
		self.config.set('Settings', 'UserTimezone', str(self.get_timezone_diff()))
		self.config.set('Units', 'KelvinToCelcius', '273.15')

		with open(os.path.join(self.init_dir, 'config.ini'), 'w') as f:
			self.config.write(f)

		self.do_init()


	def do_init(self):

		self.root_directory = self.config.get('Directories', 'RootDirectory')
		self.entry_point = self.config.get('Application', 'EntryPoint')
		self.init_dir = self.config.get('Directories', 'InitDirectory')
		self.data_directory = self.config.get('Directories', 'DataDirectory')
		self.csv_directory = self.config.get('Directories', 'CsvDirectory')
		self.json_directory = self.config.get('Directories', 'JsonDirectory')
		self.log_directory = self.config.get('Directories', 'LogDirectory')
		self.backup_directory = self.config.get('Directories', 'BackupDirectory')
		self.api_key_path = self.config.get('Paths', 'ApiKeyFile')
		self.secret_key_path = self.config.get('Paths', 'SecretKeyFile')
		self.csv_on = self.config.getboolean('Flags', 'CsvOn')
		self.json_on = self.config.getboolean('Flags', 'JsonOn')
		self.log_on = self.config.getboolean('Flags', 'LogOn')

		self.create_backup_dir_if_not_exists()
		self.create_log_dir_if_not_exists()
		self.create_csv_dir_if_not_exists()
		self.create_raw_data_dir_if_not_exists()

	
	@staticmethod
	def create_dir_if_not_exists(DIR_NAME):

		try:
			if not os.path.exists(DIR_NAME):
				os.makedirs(DIR_NAME)

		except:
			raise Exception

	def create_backup_dir_if_not_exists(self):

		try:
			Initializer.create_dir_if_not_exists(self.backup_directory)

		except Exception as error:
			print(error_message('ServiceOptions.create_backup_dir_if_not_exists(self)', error))
			self.logMe.write(error_message('ServiceOptions.create_backup_dir_if_not_exists(self)', error))

	def create_log_dir_if_not_exists(self):

		if self.log_on:
			try:
				Initializer.create_dir_if_not_exists(self.log_directory)

			except Exception as error:
				print(error_message('ServiceOptions.create_log_dir_if_not_exists(self)', error))
				self.logMe.write(error_message('ServiceOptions.create_log_dir_if_not_exists(self)', error))

	def create_csv_dir_if_not_exists(self):

		if self.csv_on:
			try:
				Initializer.create_dir_if_not_exists(self.csv_directory)

			except Exception as error:
				print(error_message('ServiceOptions.create_csv_dir_if_not_exists(self)', error))
				self.logMe.write(error_message('ServiceOptions.create_csv_dir_if_not_exists(self)', error))

	def create_raw_data_dir_if_not_exists(self):

		try:
			Initializer.create_dir_if_not_exists(self.data_directory)

		except Exception as error:
			print(error_message('ServiceOptions.create_raw_data_dir_if_not_exists(self)', error))
			self.logMe.write(error_message('ServiceOptions.create_raw_data_dir_if_not_exists(self)', error))

	def load_secret_key(self) -> str:
		'''Load the secret key for CryptoSymmetric encryption, if secret key is
		previously generated. If not, generate the secret key, save into a 
		file and then load it into memory and return it as string.'''

		secret_key = None

		if os.path.isfile(self.secret_key_path):
			with open(self.secret_key_path, 'rb') as f:
				secret_key = f.read()
		else:
			secret_key = CryptoSymmetric.generate_key()
			with open(self.secret_key_path, 'wb') as f:
				f.write(secret_key)

		return secret_key.decode()

	def load_api_key(self) -> str:

		api_key = None

		if not os.path.isfile(self.api_key_path):
			raise ApiKeyNotFoundError()
		
		secret_key = self.load_secret_key()

		with open(self.api_key_path, 'rb') as f:
			decrypted_api_key = f.read()
			api_key = CryptoSymmetric.decrypt_message(decrypted_api_key, secret_key)

		return api_key
	
	def save_api_key(self, api_key):

		secret_key = self.load_secret_key()
		encrypted_api_key = CryptoSymmetric.encrypt_message(api_key, secret_key)

		with open(self.api_key_path, 'wb') as f:
			f.write(encrypted_api_key)

	def add_cron_job(self):

		cmd = f'(crontab -l ; echo "0,30 * * * * python3 {os.path.join(self.root_directory, self.entry_point)}") 2>&1 | grep -v "no crontab" | uniq | crontab -'
		run(cmd, shell=True)

	def get_timezone_diff(self) -> int:

		localtz = dateutil.tz.tzlocal()
		localoffset = localtz.utcoffset(datetime.now(localtz))
		
		return int(localoffset.total_seconds() / 3600)
