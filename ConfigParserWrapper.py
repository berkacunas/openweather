import os
from configparser import ConfigParser

class ConfigParserWrapper:
	
	def __init__(self):
		
		cwd = os.getcwd()
		init_dir = os.path.join(cwd, '.init')
		self.config_path = os.path.join(init_dir, 'config.ini')

		if (os.path.exists(init_dir)) and (not os.path.isfile(self.config_path)):
			with open(self.config_path, 'x') as f:
				f.close()
		
		self.config = ConfigParser()
		self.config.read(self.config_path)
		
	def get(self, section: str, option: str) -> str:
		
		return self.config.get(section, option)
	
	def getint(self, section: str, option: str) -> int:
		
		return self.config.getint(section, option)
	
	def getfloat(self, section: str, option: str) -> float:
		
		return self.config.getfloat(section, option)
	
	def getboolean(self, section: str, option: str) -> bool:
		
		return self.config.getboolean(section, option)

	def add_section(self, section: str):
		
		self.config.add_section(section)
		
	def has_section(self, section: str) -> bool:
		
		return self.config.has_section(section)
		
	def remove_section(self, section: str) -> bool:
		
		return self.config.remove_section(section)

	def set(self, section: str, option: str, value):
		
		self.config.set(section, option, str(value))
		
	def write(self):
		
		with open(self.config_path, "w") as f:
			self.config.write(f)
			
	def remove_option(self, section: str, option: str) -> bool:
		
		return self.config.remove_option(section, option)
