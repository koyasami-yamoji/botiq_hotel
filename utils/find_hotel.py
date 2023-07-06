from database import add_to_bd
from loader import bot
from loguru import logger
from utils.api_request import api_request
from utils.proccesing_json import get_hotels, hotel_info
from telebot.types import InputMediaPhoto


def find_hotel(message, data) -> None:
	"""
	Формирования запроса об отеле и отправка запроса.
	Вывод полученной информации пользователю
	:param message: Message
	:param data: Dict Данные собранные от пользователя
	:return: None
	"""
	payload = {
		"currency": "USD",
		"eapid": 1,
		"locale": "en_US",
		"siteId": 300000001,
		"destination": {
			"regionId": str(data['destination_id'])
		},
		"checkInDate": {
			"day": int(data['checkInDate']['day']),
			"month": int(data['checkInDate']['month']),
			"year": int(data['checkInDate']['year'])
		},
		"checkOutDate": {
			"day": int(data['checkOutDate']['day']),
			"month": int(data['checkOutDate']['month']),
			"year": int(data['checkOutDate']['year'])
		},
		"rooms": [
			{
				"adults": 2,
				"children": [{"age": 5}, {"age": 7}]
			}
		],
		"resultsStartingIndex": 0,
		"resultsSize": 200,
		"sort": data['sort'],
		"filters": {
			"price": {
				"max": int(data['max_price']),
				"min": int(data['min_price'])
			}
		}
	}

	url = "https://hotels4.p.rapidapi.com/properties/v2/list"
	response_hotels = api_request('POST', url, payload)
	logger.info(f'Сервер вернул ответ {response_hotels.status_code}. User_id {message.chat.id}')

	if response_hotels.status_code == 200:
		hotels = get_hotels(response_hotels.text, data['command'], data['min_distance'], data['max_distance'])

		if 'error' in hotels:
			bot.send_message(message.chat.id, f'{hotels["error"]}\n Ошибка, попробуйте ввести другие параметры')

		count = 0
		for hotel in hotels.values():
			if count < int(data['count_hotels']):
				count += 1
				payload = {
					"currency": "USD",
					"eapid": 1,
					"locale": "en_US",
					"siteId": 300000001,
					"propertyId": hotel['id']
				}
				summary_url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"
				summary_response = api_request("POST", url=summary_url, params=payload)
				logger.info(f'Сервер вернул ответ статус запроса {summary_response.status_code}. User_id {message.chat.id}')
				if summary_response.status_code == 200:
					summary_info = hotel_info(summary_response.text)
					caption = f"Название отеля: {hotel['name']}.\n" \
							  f"Адрес: {summary_info['address']}.\n" \
							  f"Расстояние до центра: {round(hotel['distance'], 2)} Миль." \
							  f"Стоимость проживания в сутки {hotel['price']}"

					medias = []
					if int(data['count_photo']) > 0:
						images_url = [summary_info['images'][url] for url in range(int(data['count_photo']))]
					else:
						images_url = None

					data_for_database = {
						hotel['id']: {
							'name': hotel['name'],
							'address': summary_info['address'],
							'user_id': message.chat.id,
							'price': hotel['price'],
							'distance': round(hotel['distance'], 2),
							'date_time': data['date_time'],
							'images': images_url

						}
					}
					add_to_bd.add_response(data_for_database)

					if images_url:
						for num, url in enumerate(images_url):
							medias.append(InputMediaPhoto(media=url))

						logger.info(f'Вывод в чат информацию о отеле. User_id {message.chat.id}')
						bot.send_message(message.chat.id, caption)
						bot.send_media_group(message.chat.id, media=medias)
					else:
						logger.info(f'Вывод в чат информацию о отеле. User_id {message.chat.id}')
						bot.send_message(message.chat.id, caption)
				else:
					logger.error(f'Что-то пошло не так. Код ошибки {response_hotels.status_code}')
					bot.send_message(message.chat.id, f'Что-то пошло не так. Код ошибки {summary_response.status_code}')

			else:
				break
	else:
		logger.error(f'Что-то пошло не так. Код ошибки {response_hotels.status_code}')
		bot.send_message(message.chat.id, f'Что-то пошло не так. Код ошибки {response_hotels.status_code}')
	logger.info(f'Поиск окончен User_id {message.chat.id}')
	bot.send_message(message.chat.id, 'Поиск окончен!')
	bot.set_state(message.chat.id, None)



