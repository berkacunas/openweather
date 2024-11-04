from abc import ABC, abstractmethod

class CRUD(ABC):
	'''Interface class for all CRUD classes'''
 
	@abstractmethod
	def load_tuple(self, item): raise NotImplementedError(f'Interface class load_tuple method must be overriden')
 
	@abstractmethod
	def select(self): raise NotImplementedError(f'Interface class select method must be overriden')
 
	@abstractmethod
	def insert(self): raise NotImplementedError(f'Interface class insert method must be overriden')
 
	@abstractmethod
	def update(self): raise NotImplementedError(f'Interface class update method must be overriden')
 
	@abstractmethod
	def delete(self): raise NotImplementedError(f'Interface class delete method must be overriden')
 
	@abstractmethod
	def select_all() -> list: raise NotImplementedError(f'Interface class select_all method must be overriden')
 
	@abstractmethod
	def get_id(self): raise NotImplementedError(f'Interface class get_id method must be overriden')
