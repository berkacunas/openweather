import os
from datetime import datetime
import dateutil.tz
from subprocess import run
from ConfigParserWrapper import ConfigParserWrapper

from OpenWeatherException import ApiKeyNotFoundError, ApiKeyDuplicateError
import CryptoSymmetric
from LogMe import LogMe, error_message

class Initializer:

	def __init__(self, cwd):

		self.cwd = cwd
		self.init_dir = os.path.join(cwd, '.init')
		self.inited = os.path.exists(self.init_dir)

		self.config_wrapper = ConfigParserWrapper()
		self.logMe = LogMe()

		if not os.path.exists(self.init_dir):
			return 

		self.do_init()

	def init(self, cwd):

		if os.path.exists(self.init_dir):
			return 
	
		os.mkdir(self.init_dir)
		
		self.config_wrapper.add_section('Directories')
		self.config_wrapper.add_section('Application')
		self.config_wrapper.add_section('Service')
		self.config_wrapper.add_section('Paths')
		self.config_wrapper.add_section('Flags')
		self.config_wrapper.add_section('OpenWeather.Server')
		self.config_wrapper.add_section('OpenWeather.Resources.Json')
		self.config_wrapper.add_section('Database')
		self.config_wrapper.add_section('Database.MySQL')
		self.config_wrapper.add_section('Data')
		self.config_wrapper.add_section('Settings')
		self.config_wrapper.add_section('Units')
		self.config_wrapper.set('Directories', 'RootDirectory', self.cwd)
		self.config_wrapper.set('Directories', 'InitDirectory', self.init_dir)
		self.config_wrapper.set('Directories', 'DataDirectory', os.path.join(self.cwd, 'data'))
		self.config_wrapper.set('Directories', 'CsvDirectory', os.path.join(self.cwd, 'csv'))
		self.config_wrapper.set('Directories', 'JsonDirectory', os.path.join(self.cwd, 'json'))
		self.config_wrapper.set('Directories', 'LogDirectory', os.path.join(self.cwd, 'log'))
		self.config_wrapper.set('Directories', 'BackupDirectory', os.path.join(self.cwd, 'backup'))
		self.config_wrapper.set('Application', 'EntryPoint', '__main__.py')
		self.config_wrapper.set('Service', 'Daemon', 'False')
		self.config_wrapper.set('Paths', 'ApiKeyFile', os.path.join(self.cwd, 'data', 'api.key'))
		self.config_wrapper.set('Paths', 'SecretKeyFile', os.path.join(self.cwd, 'data', 'secret.key'))
		self.config_wrapper.set('Paths', 'DbSchemaFile', os.path.join(self.cwd, 'data', 'openweather-mysql-schema.sql'))
		self.config_wrapper.set('Paths', 'DbSchemaBackupFile', os.path.join(self.cwd, 'data', 'openweather-mysql-schema.sql.backup'))
		self.config_wrapper.set('Flags', 'JsonOn', 'False')
		self.config_wrapper.set('Flags', 'CsvOn', 'False')
		self.config_wrapper.set('Flags', 'LogOn', 'True')
		self.config_wrapper.set('OpenWeather.Server', 'Url', 'https://api.openweathermap.org/data/2.5/weather?')
		self.config_wrapper.set('OpenWeather.Resources.Json', 'CityList', os.path.join(self.cwd, 'resources', 'city.list.json'))
		self.config_wrapper.set('OpenWeather.Resources.Json', 'CurrentCityList', os.path.join(self.cwd, 'resources', 'current.city.list.json'))
		self.config_wrapper.set('OpenWeather.Resources.Csv', 'CountryCodes', os.path.join(self.cwd, 'resources', 'country_codes.csv'))
		self.config_wrapper.set('Database', 'Created', 'False')
		self.config_wrapper.set('Database', 'Enabled', 'False')
		self.config_wrapper.set('Database.MySQL', 'Host', '')
		self.config_wrapper.set('Database.MySQL', 'DbName', '')
		self.config_wrapper.set('Database.MySQL', 'Username', '')
		self.config_wrapper.set('Database.MySQL', 'Password', '')
		self.config_wrapper.set('Database.MySQL', 'Port', '')
		self.config_wrapper.set('Data', 'ApiKey', '')
		self.config_wrapper.set('Data', 'CityConflictsJsonFile', os.path.join(self.cwd, 'data', 'CityNameConflicts.json'))
		self.config_wrapper.set('Settings', 'MaxGroupQueryLimit', '20')
		self.config_wrapper.set('Settings', 'UserTimezone', str(self.get_timezone_diff()))
		self.config_wrapper.set('Units', 'KelvinToCelcius', '273.15')

		self.config_wrapper.write()
		self.do_init()


	def do_init(self):

		self.root_directory = self.config_wrapper.get('Directories', 'RootDirectory')
		self.init_dir = self.config_wrapper.get('Directories', 'InitDirectory')
		self.data_directory = self.config_wrapper.get('Directories', 'DataDirectory')
		self.csv_directory = self.config_wrapper.get('Directories', 'CsvDirectory')
		self.json_directory = self.config_wrapper.get('Directories', 'JsonDirectory')
		self.log_directory = self.config_wrapper.get('Directories', 'LogDirectory')
		self.backup_directory = self.config_wrapper.get('Directories', 'BackupDirectory')
		self.entry_point = self.config_wrapper.get('Application', 'EntryPoint')
		self.is_daemon = self.config_wrapper.getboolean('Service', 'Daemon')
		self.db_enabled = self.config_wrapper.getboolean('Database', 'Enabled')
		self.api_key_path = self.config_wrapper.get('Paths', 'ApiKeyFile')
		self.secret_key_path = self.config_wrapper.get('Paths', 'SecretKeyFile')
		self.csv_on = self.config_wrapper.getboolean('Flags', 'CsvOn')
		self.json_on = self.config_wrapper.getboolean('Flags', 'JsonOn')
		self.log_on = self.config_wrapper.getboolean('Flags', 'LogOn')

		self.create_backup_dir_if_not_exists()
		self.create_log_dir_if_not_exists()
		self.create_csv_dir_if_not_exists()
		self.create_json_dir_if_not_exists()

	
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

	def create_json_dir_if_not_exists(self):

		if self.json_on:
			try:
				Initializer.create_dir_if_not_exists(self.json_directory)

			except Exception as error:
				print(error_message('ServiceOptions.create_json_dir_if_not_exists(self)', error))
				self.logMe.write(error_message('ServiceOptions.create_json_dir_if_not_exists(self)', error))

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

		encrypted_api_key = self.config_wrapper.get('Data', 'ApiKey')
		if len(encrypted_api_key) == 0:
			raise ApiKeyNotFoundError('Api key not found.')
		
		secret_key = self.load_secret_key()
		api_key = CryptoSymmetric.decrypt_message(encrypted_api_key, secret_key)

		return api_key
	
	def save_api_key(self, api_key):

		secret_key = self.load_secret_key()
		encrypted_api_key = CryptoSymmetric.encrypt_message(api_key, secret_key)
		
		self.config_wrapper.set('Data', 'ApiKey', encrypted_api_key.decode('UTF-8'))
		self.config_wrapper.write()


	def add_cron_job(self) -> bool:

		if not self.is_daemon:
			cmd = f'(crontab -l ; echo "0,30 * * * * python3 {os.path.join(self.root_directory, self.entry_point)}") 2>&1 | grep -v "no crontab" | uniq | crontab -'
			run(cmd, shell=True)

			self.is_daemon = True
			self.config_wrapper.set('Service', 'Daemon', self.is_daemon)
			self.config_wrapper.write()

	def get_timezone_diff(self) -> int:

		localtz = dateutil.tz.tzlocal()
		localoffset = localtz.utcoffset(datetime.now(localtz))
		
		return int(localoffset.total_seconds() / 3600)
