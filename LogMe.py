'''	module info
# Filename: LogMe
# Extension: py
# Version: 0.02
# Project: LogMe
# Description: Library module for logging
# Creator: Berk Acunaş
# Created on: 2023.11.07
'''
''' seperation of files
	filename.xxx				created		xxxx.xx.xx		xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	
'''
''' dev history
	0.03		not under development	2023.10.28		#################
'''
'''	version history
	 0.01		created		2023.11.07  	LogMe module is seperated from Services.BackupMyMySQL/backup-my-mysql.pyw code into a new file.
	0.02		updated		2023.11.16		First version iteration done after module started to work completely properly without any error.
'''

import os
import sys
from enum import Enum
from collections import namedtuple
import copy

FrameInfo = namedtuple('FrameInfo', ['filename', 'lineno', 'function', 'parameters'])

def frame_info(walkback=0):
	# NOTE: sys._getframe() is a tiny bit faster than inspect.currentframe()
	#   Although the function name is prefixed with an underscore, it is
	#   documented and fine to use assuming we are running under CPython:
	#
	#   https://docs.python.org/3/library/sys.html#sys._getframe
	#
	frame = sys._getframe().f_back

	for __ in range(walkback):
		f_back = frame.f_back
		if not f_back:
			break

		frame = f_back

	return FrameInfo(frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name, copy.deepcopy(frame.f_locals))

def error_message(func_name, error):

	return f'Exception at function: {func_name}\nError message: {error}'

def info_message(func_name, info):

	return f'Success function: {func_name}\nInfo message: {info}'


class LogMe:

	def __init__(self, log_dir, filename_without_ext, ext='log') -> None:

		self.logs = []
		self.log_dir = log_dir
		self.filename_without_ext = filename_without_ext
		self.ext = ext
		self.log_filename = os.path.join(self.log_dir, f'{self.filename_without_ext}.{self.ext}') 

	def write(self, filename=None):
	
		if len(self.logs) == 0:
			return
		
		try:
			log_text = ''
			
			mode = None
			if os.path.exists(self.log_filename):
				mode = 'a'
			else:
				mode = 'w'
				f = open(self.log_filename, 'x')
				f.close()
			
			newline = ''
			with open(self.log_filename, mode) as f:
				if f.tell() != 0:
					newline = '\n'

				for log in self.logs:
					log_text = newline + log
					f.write(log_text)

				f.write('\n')
				f.write('*' * 120)
				
			self.logs.clear()
		
		except Exception as error:
			print(error_message('LogMe.write(filename=None)', error))
			self.logs.append(error_message('LogMe.write(filename=None)', error))
   
		else:
			print(info_message('LogMe.write(filename=None)', 'Log file is written.'))
			self.logs.append(info_message('LogMe.write(filename=None)', 'Log file is written.'))
  
  