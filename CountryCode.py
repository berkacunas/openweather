import csv
from ConfigParserWrapper import ConfigParserWrapper

class CountryCode:

    config_wrapper = ConfigParserWrapper()

    @staticmethod
    def get_country_code(country_name):

        country_code = None
        country_code_file = CountryCode.config_wrapper.get('OpenWeather.Resources.Csv', 'CountryCodes')

        with open(country_code_file, 'r', encoding='UTF-8') as f:
            country_code = CountryCode._query_rows(f, 'country', 'alpha2_code', country_name)
            
        return country_code
        
    @staticmethod
    def get_country_name(country_code):

        country_name = None
        country_code_file = CountryCode.config_wrapper.get('OpenWeather.Resources.Csv', 'CountryCodes')

        with open(country_code_file, 'r', encoding='UTF-8') as f:
            country_name = CountryCode._query_rows(f, 'alpha2_code', 'country', country_code)

        return country_name

    @staticmethod
    def _query_rows(f, search_column: str, return_column: str, keyword: str) -> str:

        reader = csv.DictReader(f, delimiter=',', fieldnames = ['id', 'country', 'alpha2_code', 'alpha3_code', 'numeric'])

        for row in reader:
            if row[search_column] == keyword:
                return row[return_column]
            
        return None