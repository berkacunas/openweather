class UnhandledLogicError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors

class MessagePrintError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors

class CityNotFoundError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors
  
class TimezoneError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors

class TupleLoadingError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors

class LoggingFileError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors

class OpenWeatherLoggerNotMarkedError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors

class ServerDataIsEmptyError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors

class ApiKeyNotFoundError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors

class ApiKeyDuplicateError(Exception):
	def __init__(self, message=None, errors=None):     
	   
		super().__init__(message)
		self.errors = errors