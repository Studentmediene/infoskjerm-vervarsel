import xml.etree.ElementTree as ET

import requests

class WeatherData:
    def __init__(self):
        self.XML_URL = "http://www.yr.no/sted/Norge/S%C3%B8r-Tr%C3%B8ndelag/Trondheim/Trondheim/varsel.xml"
        self.xml = None
        self.first_time = None

    def populate(self):
        r = requests.get(self.XML_URL)
        r.raise_for_status()
        self.xml = ET.fromstring(r.text)
        self.first_time = self.xml.find("./forecast/tabular/time")

    def get_time(self):
        period = int(self.first_time.attrib['period'])
        period_map_to_str = {
            0: "i natt",
            1: "denne morgenen",
            2: "i dag",
            3: "i kveld",
        }
        return period_map_to_str[period]

    def get_symbol(self):
        symbol_elem = self.first_time.find("./symbol")
        return symbol_elem.attrib['var']

    def get_temperature(self):
        temperature_elem = self.first_time.find("./temperature")
        return int(temperature_elem.attrib['value'])

