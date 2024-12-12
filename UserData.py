import os
import json
from decimal import Decimal

from ConfigParserWrapper import ConfigParserWrapper

class UserData:
    '''This class manage data on a json file instead of database.'''

    

    def __init__(self):

        self.data = {}

        self.config_wrapper = ConfigParserWrapper()
        self.userdata_json_path = self.config_wrapper.get('Data', 'UserDataFile')

        self._create_file_if_not_exists()
        self.load()

    def _create_file_if_not_exists(self):
        
        if not os.path.exists(self.userdata_json_path):
            self.save()

    def load(self):

        with open(self.userdata_json_path, 'r', encoding='UTF-8') as f:
            self.data = json.load(f)

    def save(self):

        # Serialize dictionary into an object.
        json_object = json.dumps(self.data, indent=4, default=self.decimal_serializer)
        with open(self.userdata_json_path, 'w', encoding='UTF-8') as f:
            f.write(json_object)

    def decimal_serializer(self, obj):

        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError('Type is not serializable')