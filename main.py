import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import json
import os
import logging
from countries import get_available_countries
from tqdm import tqdm

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('gismeteo.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)



class GismeteoParser:
    def __init__(self, country):
        self.base_url = "https://www.gismeteo.ru"
        self.country = country.lower()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.all_data = []

    def get_available_countries(self) -> dict:
        """Получаем список доступных стран с их структурой"""
        return get_available_countries()

    def get_regions(self, url: str) -> list:
        """Получает регионы для стран с 3 уровнями"""
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        regions = []

        items = soup.find_all('div', class_='item')
        for item in items:
            links = item.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                name = link.get_text(strip=True)
                # Match region links of the form /sitemap/{self.country}/<region>/
                if (
                    href and name and
                    href.startswith(f'/sitemap/{self.country}/') and
                    href.count('/') == 4
                ):
                    full_url = urljoin(self.base_url, href)
                    regions.append({
                        'name': name,
                        'url': full_url,
                        'href': href
                    })

        return regions

    def get_districts(self, region_url: str, region_name: str) -> list:
        """Получает районы для регионов (для стран с 3 уровнями)"""
        time.sleep(0.5)
        try:
            response = self.session.get(region_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            districts = []

            items = soup.find_all('div', class_='item')
            for item in items:
                links = item.find_all('a', href=lambda x: x and f'/sitemap/{self.country}/' in x)
                for link in links:
                    href = link.get('href')
                    name = link.get_text(strip=True)
                    if href and name:
                        full_url = urljoin(self.base_url, href)
                        districts.append({
                            'name': name,
                            'url': full_url
                        })

            return districts
        except Exception as e:
            print(f"        Ошибка при получении районов: {e}")
            return []

    def get_cities_from_page(self, url: str, location_name: str) -> list:
        """Получает города со страницы"""
        time.sleep(0.5)
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            cities = []
            content_column = soup.find('div', class_='content-column')
            if content_column:
                links = content_column.find_all('a', href=True)
                for link in links:
                    name = link.get_text(strip=True)
                    if name and len(name) > 1:
                        cities.append(name)

            cities = list(dict.fromkeys(cities))
            print(f"        Найдено городов: {len(cities)}")
            return cities

        except Exception as e:
            print(f"        Ошибка при получении городов: {e}")
            return []

    def parse_level_1_structure(self, url: str, country_name: str) -> list:
        """Парсинг для стран с 1 уровнем (только города)"""
        print(f"    Структура: только города")
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        cities = []
        content_column = soup.find('div', class_='content-column')
        if content_column:
            links = content_column.find_all('a', href=True)
            for link in links:
                name = link.get_text(strip=True)
                if name and len(name) > 1:
                    cities.append(name)

        return [{
            'region': country_name,
            'districts': [{
                'district': 'Все города',
                'cities': list(dict.fromkeys(cities))
            }]
        }]

    def parse_level_2_structure(self, url: str, country_name: str) -> list:
        """Парсинг для стран с 2 уровнями (районы -> города)"""
        print(f"    Структура: районы -> города")
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        regions_data = []
        items = soup.find_all('div', class_='item')

        print()  # отступ перед прогресс-баром
        for item in tqdm(items, desc='Районы', unit='район'):
            links = item.find_all('a', href=lambda x: x and f'/sitemap/{self.country}/' in x)
            for link in links:
                href = link.get('href')
                name = link.get_text(strip=True)
                if href and name:
                    full_url = urljoin(self.base_url, href)

                    print(f"    Парсим район: {name} ")
                    cities = self.get_cities_from_page(full_url, name)

                    region_data = {
                        'region': name,
                        'districts': [{
                            'district': 'Населенные пункты',
                            'cities': cities
                        }]
                    }
                    regions_data.append(region_data)

        return regions_data

    def parse_level_3_structure(self, url: str, country_name: str) -> list:
        """Парсинг для стран с 3 уровнями (регионы -> районы -> города)"""
        print(f"    Структура: регионы -> районы -> города")
        regions = self.get_regions(url)
        regions_data = []

        print()  # отступ перед прогресс-баром
        for region in tqdm(regions, desc='Регионы', unit='регион'):
            print(f"    Парсим регион: {region['name']} ")

            region_data = {
                'region': region['name'],
                'districts': []
            }

            districts = self.get_districts(region['url'], region['name'])

            print()  # отступ перед прогресс-баром
            for district in tqdm(districts, desc=f"  Районы {region['name']}", unit='район'):
                print(f"      Парсим район: {district['name']} ")
                cities = self.get_cities_from_page(district['url'], district['name'])

                district_data = {
                    'district': district['name'],
                    'cities': cities
                }

                region_data['districts'].append(district_data)

            regions_data.append(region_data)

        return regions_data

    def parse_country(self, max_regions: int = None, max_districts: int = None) -> list:
        """Парсит выбранную страну используя предустановленную структуру"""
        countries = self.get_available_countries()
        if self.country not in countries:
            print(f"Страна '{self.country}' не найдена!")
            return []

        country_info = countries[self.country]
        country_name = country_info['name']
        country_levels = country_info['levels']
        country_structure = country_info['structure']
        country_url = f"{self.base_url}/sitemap/{self.country}/"

        logging.info(f"Начат парсинг страны: {country_name.upper()}")
        print("\n" + "=" * 60)
        print(f"ПАРСИНГ СТРАНЫ: {country_name.upper()}")
        print("=" * 60)

        # Используем предустановленную структуру вместо автоматического определения
        structure_descriptions = {
            1: "только города",
            2: "районы -> города",
            3: "регионы -> районы -> города"
        }

        print(f"    Используем структуру: {country_structure} ({structure_descriptions[country_levels]})")
        logging.info(
            f"Используем структуру: {country_structure} ({structure_descriptions[country_levels]})"
        )

        # Парсим в зависимости от предустановленной структуры
        try:
            if country_levels == 1:
                self.all_data = self.parse_level_1_structure(country_url, country_name)
            elif country_levels == 2:
                self.all_data = self.parse_level_2_structure(country_url, country_name)
            else:  # levels == 3
                self.all_data = self.parse_level_3_structure(country_url, country_name)
        except Exception as e:
            logging.error(f"Ошибка во время парсинга: {e}")
            raise

        # Применяем ограничения если нужно
        if max_regions and len(self.all_data) > max_regions:
            self.all_data = self.all_data[:max_regions]
            print(f"    Ограничение: обработано {max_regions} регионов")
            logging.info(f"Ограничение: обработано {max_regions} регионов")

        logging.info(f"Парсинг завершён. Всего регионов: {len(self.all_data)}")
        return self.all_data


    def save_partial_results(self) -> None:
        """Сохраняет промежуточные результаты"""
        filename = f"gismeteo_{self.country}_partial.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)

    def save_final_results(self) -> str:
        """Сохраняет финальные результаты в JSON"""
        filename = f"gismeteo_{self.country}_final.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        return filename

    def export_to_txt(self) -> str:
        """Экспортирует результаты в текстовый файл"""
        filename = f"gismeteo_{self.country}_results.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for region in self.all_data:
                f.write(f"- {region['region']}\n")
                for district in region['districts']:
                    f.write(f"- - {district['district']}\n")
                    for city in district['cities']:
                        f.write(f"- - - {city}\n")

        return filename

    def verify_data_integrity(self) -> tuple:
        """Проверяет целостность данных"""
        total_regions = len(self.all_data)
        total_districts = sum(len(region['districts']) for region in self.all_data)
        total_cities = sum(len(district['cities']) for region in self.all_data for district in region['districts'])

        return total_regions, total_districts, total_cities

    def print_statistics(self) -> None:
        """Выводит статистику"""
        regions, districts, cities = self.verify_data_integrity()
        countries = self.get_available_countries()
        country_info = countries[self.country]

        print(f"\n{'=' * 60}")
        print("СТАТИСТИКА ПАРСИНГА:")
        print(f"{'=' * 60}")
        print(f"Страна: {country_info['name']}")
        print(f"Структура: {country_info['structure']} ({country_info['levels']} уровня)")
        print(f"Регионов/районов: {regions}")
        print(f"Областей/подрайонов: {districts}")
        print(f"Городов/населенных пунктов: {cities}")
        print(f"{'=' * 60}")


def show_available_countries_numbered() -> list:
    """
    Показывает доступные страны с номерами
    """
    countries = get_available_countries()
    levels_desc = {
        1: "только города",
        2: "районы -> города",
        3: "регионы -> районы -> города"
    }
    print("\nДОСТУПНЫЕ СТРАНЫ ДЛЯ ПАРСИНГА:")
    print("-" * 60)
    country_list = list(countries.items())
    for idx, (eng_name, info) in enumerate(country_list, 1):
        print(f"{idx} - {info['name']:12} ({levels_desc[info['levels']]})")
    print("-" * 60)
    return country_list


def get_user_country() -> str | None:
    """Запрашивает у пользователя выбор страны по номеру"""
    country_list = show_available_countries_numbered()
    while True:
        try:
            choice = input("\nВведите число страны: ").strip()
        except KeyboardInterrupt:
            return None
        if not choice.isdigit():
            print("Ошибка: введите номер страны!")
            continue
        idx = int(choice)
        if 1 <= idx <= len(country_list):
            eng_name, _ = country_list[idx-1]
            return eng_name
        else:
            print("Ошибка: такого номера нет в списке!")
            continue


def main() -> None:
    """Основная функция"""
    try:
        print(f"{'=' * 60}")
        print("           УМНЫЙ ПАРСЕР GISMETEO")
        print(f"{'=' * 60}")

        country = get_user_country()
        if not country:
            return

        parser = GismeteoParser(country)

        results = parser.parse_country()

        if results:
            # Сохраняем только нужные форматы
            final_json = parser.save_final_results()
            txt_file = parser.export_to_txt()

            parser.print_statistics()

            print(f"\nРЕЗУЛЬТАТЫ СОХРАНЕНЫ:")
            print(f"  • {final_json} - данные в JSON формате")
            print(f"  • {txt_file} - данные в текстовом формате")

            # Удаляем временный файл
            partial_file = f"gismeteo_{country}_partial.json"
            if os.path.exists(partial_file):
                os.remove(partial_file)
                print(f"  • {partial_file} - временный файл удален")

            print(f"\nПарсинг успешно завершен!")
        else:
            print("Парсинг не удался.")
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем. Завершение работы.")
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()