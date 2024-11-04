class UnhandledLogicError(Exception):
	def __init__(self, message, errors):     
	   
		super().__init__(message)
		self.errors = errors

class MessagePrintError(Exception):
	def __init__(self, message, errors):     
	   
		super().__init__(message)
		self.errors = errors

class CityNotFoundError(Exception):
	def __init__(self, message, errors):     
	   
		super().__init__(message)
		self.errors = errors
  
class TimezoneError(Exception):
	def __init__(self, message, errors):     
	   
		super().__init__(message)
		self.errors = errors

class TupleLoadingError(Exception):
	def __init__(self, message, errors):     
	   
		super().__init__(message)
		self.errors = errors
		