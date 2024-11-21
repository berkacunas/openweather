import os
from datetime import datetime
import subprocess
from configparser import ConfigParser
from subprocess import run

from OpenWeatherException import ApiKeyNotFoundError, ApiKeyDuplicateError
import CryptoSymmetric
from LogMe import LogMe, error_message

class Initializer:

	def __init__(self):

		self.logMe = LogMe()
		
		config = ConfigParser()
		config.read('serviceconfig.ini')
		
		self.root_directory = config.get('Directories', 'rootdirectory')
		self.entry_point = config.get('Application', 'EntryPoint')
		self.backup_directory = config.get('Directories', 'BackupDirectory')
		self.log_directory = config.get('Directories', 'LogDirectory')
		self.csv_directory = config.get('Directories', 'CsvDirectory')
		self.rawdata_directory = config.get('Directories', 'RawDataDirectory')

		self.api_key_path = config.get('Paths', 'ApiKeyFile')
		self.secret_key_path = config.get('Paths', 'SecretKeyFile')

		self.log_on = config.getboolean('Flags', 'LogOn')
		self.csv_on = config.getboolean('Flags', 'CsvOn')

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
			Initializer.create_dir_if_not_exists(self.rawdata_directory)

		except Exception as error:
			print(error_message('ServiceOptions.create_raw_data_dir_if_not_exists(self)', error))
			self.logMe.write(error_message('ServiceOptions.create_raw_data_dir_if_not_exists(self)', error))

	@staticmethod
	def get_hostname() -> str:

		cmd = 'hostname'
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()

		return output.decode('UTF-8').replace('\n', '')
	
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

