# Тестирует получение регионов.

import unittest
from main import GismeteoParser

class TestGismeteoParser(unittest.TestCase):
    def setUp(self):
        self.parser = GismeteoParser('russia')

    def test_get_regions_returns_list(self):
        regions = self.parser.get_regions('https://www.gismeteo.ru/sitemap/russia/')
        self.assertIsInstance(regions, list)
        self.assertGreater(len(regions), 0)

if __name__ == '__main__':
    unittest.main()
