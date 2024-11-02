###################################################################
# Filename: LogMe.py
# Extension: py
# Version: 0.02
# Project: LogMe
# Description: Library module for logging
# Creator: Berk Acunaş
# Created on: 2023.11.07
###################################################################

import os
import sys
from collections import namedtuple
import copy

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

	return f'Exception => {frame_info_str} Error message: {error}'

def info_message(frame_info_str: str, info: str):

	return f'Success =>{frame_info_str} Info message: {info}'

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
			fi = frame_info()
			print(error_message(print_frame_info(fi), error))
			self.logs.append(error_message(print_frame_info(fi), error))
   
		else:
			fi = frame_info()
			print(info_message(print_frame_info(fi), 'Log file is written to disk.'))
			self.logs.append(info_message(print_frame_info(fi), 'Log file is written to disk.'))
   