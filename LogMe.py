###################################################################
# Filename: LogMe.py
# Version: 0.02
# Project: LogMe
# Description: Library module for logging.
# Creator: Berk Acunaş
# Created on: 2023.11.07
###################################################################

import os
import sys
from datetime import datetime
from configparser import ConfigParser
from collections import namedtuple
import copy

from OpenWeatherException import LoggingFileError

FrameInfo = namedtuple('FrameInfo', ['filename', 'lineno', 'function', 'parameters'])

def frame_info(walkback=0):
	
	frame = sys._getframe().f_back

	for __ in range(walkback):
		f_back = frame.f_back
		if not f_back:
			break

		frame = f_back

	return FrameInfo(frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name, copy.deepcopy(frame.f_locals))

def print_frame_info(fi):
	
	message = f'Filename: {fi.filename} Line no: {fi.lineno} Function: {fi.function}'
	
	if len(fi.parameters.items()) > 0:
		message += " Parameters: "
		for key, val in fi.parameters.items():
			message += '{} = {} '.format(key, val)
		message = message[:-1]

	print(message)
	
def error_message(frame_info_str: str, error: Exception):

	return f'{datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} Exception => {frame_info_str} Error message: {error}'

def info_message(func: str, message: str):

	return f'{datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} Success => Func: {func}   Info Message: {message}'

class LogMe:

	def __init__(self):

		self.logs = []

		config = ConfigParser()
		config.read('serviceconfig.ini')

		self.log_dir = config.get('Directories', 'LogDirectory')
		self.filename = f'{datetime.now().strftime("%Y.%m.%d")}_openweather.log'	# %Y.%m.%d %H%M%S
		self.logfile = os.path.join(self.log_dir, self.filename)

	def write(self, message):

		try:
			log_text = ''
			
			mode = None
			if os.path.exists(self.logfile):
				mode = 'a'
			else:
				mode = 'w'
				f = open(self.logfile, 'x')
				f.close()
			
			newline = ''
			with open(self.logfile, mode) as f:
				if f.tell() != 0:
					newline = '\n'

				f.write(message)
				f.write('\n')
				# f.write('*' * 120)
		
		except Exception as error:
			raise LoggingFileError(error)

	def write_collection(self, filename=None):
	
		if len(self.logs) == 0:
			return
		
		try:
			log_text = ''
			
			mode = None
			if os.path.exists(self.logfile):
				mode = 'a'
			else:
				mode = 'w'
				f = open(self.logfile, 'x')
				f.close()
			
			newline = ''
			with open(self.logfile, mode) as f:
				if f.tell() != 0:
					newline = '\n'

				for log in self.logs:
					log_text = newline + log
					f.write(log_text)

				f.write('\n')
				# f.write('*' * 120)
				
			self.logs.clear()
		
		except Exception as error:
			raise LoggingFileError(error)
