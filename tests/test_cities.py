# Tестирует получение городов

import unittest
from main import GismeteoParser

class TestGismeteoParser(unittest.TestCase):
    def setUp(self):
        self.parser = GismeteoParser('andorra')

    def test_get_cities_from_page_returns_list(self):
        # Пример: взять ссылку на район Андорры
        regions = self.parser.get_regions('https://www.gismeteo.ru/sitemap/andorra/')
        if regions:
            districts = self.parser.get_districts(regions[0]['url'], regions[0]['name'])
            if districts:
                cities = self.parser.get_cities_from_page(districts[0]['url'], districts[0]['name'])
                self.assertIsInstance(cities, list)
            else:
                self.skipTest('Нет районов для Андорры')
        else:
            self.skipTest('Нет регионов для Андорры')

if __name__ == '__main__':
    unittest.main()
