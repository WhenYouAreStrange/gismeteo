def get_available_countries():
    """Возвращает словарь доступных стран с их структурой"""
    countries = {
        'russia': {'name': 'Россия', 'levels': 3, 'structure': 'regions_districts_cities'},
        'ukraine': {'name': 'Украина', 'levels': 3, 'structure': 'regions_districts_cities'},
        'belarus': {'name': 'Беларусь', 'levels': 3, 'structure': 'regions_districts_cities'},
        'kazakhstan': {'name': 'Казахстан', 'levels': 3, 'structure': 'regions_districts_cities'},
        'moldova': {'name': 'Молдова', 'levels': 2, 'structure': 'districts_cities'},
        'uzbekistan': {'name': 'Узбекистан', 'levels': 2, 'structure': 'districts_cities'},
        'armenia': {'name': 'Армения', 'levels': 2, 'structure': 'districts_cities'},
        'azerbaijan': {'name': 'Азербайджан', 'levels': 2, 'structure': 'districts_cities'},
        'georgia': {'name': 'Грузия', 'levels': 2, 'structure': 'districts_cities'},
        'latvia': {'name': 'Латвия', 'levels': 2, 'structure': 'districts_cities'},
        'lithuania': {'name': 'Литва', 'levels': 2, 'structure': 'districts_cities'},
        'estonia': {'name': 'Эстония', 'levels': 2, 'structure': 'districts_cities'},
        'kyrgyzstan': {'name': 'Кыргызстан', 'levels': 2, 'structure': 'districts_cities'},
        'tajikistan': {'name': 'Таджикистан', 'levels': 3, 'structure': 'regions_districts_cities'},
        'turkmenistan': {'name': 'Туркменистан', 'levels': 2, 'structure': 'districts_cities'},
        'bermuda': {'name': 'Бермуды', 'levels': 1, 'structure': 'districts_cities'},
        'angola': {'name': 'Ангола', 'levels': 1, 'structure': 'districts_cities'},
        'andorra': {'name': 'Андорра', 'levels': 2, 'structure': 'regions_districts_cities'},
        'germany': {'name': 'Германия', 'levels': 2, 'structure': 'districts_cities'}
    }

    return countries