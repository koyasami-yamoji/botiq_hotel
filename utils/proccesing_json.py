import json


def get_city(response_text):
	"""
	Получение городов от сервера, создание словаря с возможными городами и их идентификатором.
	:param response_text: str ответ от сервера.
	:return possible_cities : Dict возвращение словаря с возможными городами.
	"""
	possible_cities = {}
	data = json.loads(response_text)
	if not data:
		raise LookupError('Запрос пуст')
	for id_place in data['sr']:
		try:
			possible_cities[id_place['gaiaId']] = {
				"gaiaId": id_place['gaiaId'],
				"regionNames": id_place['regionNames']['fullName']
			}
		except KeyError:
			continue
		return possible_cities


def get_hotels(response_text: str, command: str, min_distance: str, max_distance: str) -> dict:
	"""
	Принимает ответ от сервера, выбранную команду сортировки, минимальное и максимальное расстояние отеля до центра
	Возвращает отсортированный словарь отелей в зависимости от команды сортировки.
	:param response_text: str ответ от сервера.
	:param command: str команда сортировки.
	:param min_distance: str минимальное значение отеля до центра.
	:param max_distance: str максимальное значение отеля до центра.
	:return: Dict Отсортированный словарь с данными об отелях.
	"""
	data = json.loads(response_text)
	if not data:
		raise LookupError('Запрос пуст')

	hotels_data = {}
	for hotel in data['data']['propertySearch']['properties']:
		try:
			hotels_data[hotel['id']] = {
				'name': hotel['name'], 'id': hotel['id'],
				'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
				'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
				'price': hotel['price']['lead']['amount']
			}
		except (ValueError, TypeError):
			continue

	if command == '/high':
		hotels_data = {
			key: value for key, value in sorted(hotels_data.items(),
												key=lambda hotel_id: hotel_id[1]['price'], reverse=True)
		}

	elif command == '/custom':
		hotels_data = {}
		for hotel in data['data']['propertySearch']['properties']:
			if float(min_distance) < hotel['destinationInfo']['distanceFromDestination']['value'] < float(max_distance):
				try:
					hotels_data[hotel['id']] = {
						'name': hotel['name'], 'id': hotel['id'],
						'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
						'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
						'price': hotel['price']['lead']['amount']
					}
				except (ValueError, TypeError):
					continue

	return hotels_data


def hotel_info(hotels_request: str) -> dict:
	"""
	Принимает ответ от сервера с детальной информации об отеле, и возвращает словарь с данными отеля.
	:param hotels_request: str Ответ от сервера с детальной информацией.
	:return hotel_data : dict Возвращает словарь с дополнительной информацией об отеле.
	"""
	data = json.loads(hotels_request)
	if not data:
		raise LookupError('Запрос пуст')
	hotel_data = {
		'id': data['data']['propertyInfo']['summary']['id'],
		'name': data['data']['propertyInfo']['summary']['name'],
		'address': data['data']['propertyInfo']['summary']['location']['address']['addressLine'],
		'coordinates': data['data']['propertyInfo']['summary']['location']['coordinates'],
		'images': [
			url['image']['url'] for url in data['data']['propertyInfo']['propertyGallery']['images']
		]
	}

	return hotel_data