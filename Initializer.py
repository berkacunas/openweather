import os
from datetime import datetime
import subprocess
from configparser import ConfigParser

from LogMe import LogMe, error_message

class Initializer:

	def __init__(self):

		self.logMe = LogMe()
		
		config = ConfigParser()
		config.read('serviceconfig.ini')
		
		self.backup_directory = config.get('Directories', 'BackupDirectory')
		self.log_directory = config.get('Directories', 'LogDirectory')
		self.csv_directory = config.get('Directories', 'CsvDirectory')
		self.rawdata_directory = config.get('Directories', 'RawDataDirectory')

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
