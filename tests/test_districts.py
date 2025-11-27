# Тестирует получение районов

import unittest
from main import GismeteoParser

class TestGismeteoParser(unittest.TestCase):
    def setUp(self):
        self.parser = GismeteoParser('belarus')

    def test_get_districts_returns_list(self):
        # Пример: взять первый регион Беларуси для теста
        regions = self.parser.get_regions('https://www.gismeteo.ru/sitemap/belarus/')
        if regions:
            districts = self.parser.get_districts(regions[0]['url'], regions[0]['name'])
            self.assertIsInstance(districts, list)
        else:
            self.skipTest('Нет регионов для Беларуси')

if __name__ == '__main__':
    unittest.main()
