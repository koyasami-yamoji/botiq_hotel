from loader import bot
from database import add_to_bd
from states.hotel_information import HotelInfoState
from telebot.types import Message
from loguru import logger
from keyboards.inline import create_buttons
from utils.api_request import api_request
from utils.proccesing_json import get_city
from keyboards.calendar.create_calendar import Calendar
from utils.find_hotel import find_hotel
import datetime


@bot.message_handler(commands=['custom', 'lower', 'high'])
def input_command(message: Message) -> None:
	"""
	Обработчик введенной пользователем команды. "custom, lower, high"
	И запоминаем нужные данные.
	Спрашивает пользователя какой искать город.
	:param message: Message
	:return: None
	"""
	bot.set_state(message.from_user.id, HotelInfoState.input_command, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		logger.info(f'Пользователь ввел команду {message.text}, User_id {message.chat.id}')

		data['command'] = message.text
		data['chat_id'] = message.chat.id
		data['sort'] = check_command(message.text)
		data['date_time'] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')

	bot.set_state(message.from_user.id, HotelInfoState.city, message.chat.id)
	bot.send_message(message.chat.id, f'Введите город в котором хотите найти отель (На латинице)')


@bot.message_handler(state=HotelInfoState.city)
def input_city(message: Message) -> None:
	"""
	Ввод пользователем города и отправка запроса на поиск варианта городов.
	Вызов создания кнопок с городами.
	:param message: Message
	:return: None
	"""
	with bot.retrieve_data(message.chat.id) as data:
		data['city'] = message.text
		logger.info(f'Пользователь ввел город {message.text} User_id : {message.chat.id}')
		url = "https://hotels4.p.rapidapi.com/locations/v3/search"
		params = {'q': {message.text}, 'locale': 'en_US'}
		response_city = api_request('GET', url=url, params=params)
		if response_city.status_code == 200:
			logger.info(f'Сервер ответил. Статус запроса {response_city.status_code} user_id {message.chat.id}')
			possible_cities = get_city(response_city.text)
			create_buttons.show_cities_buttons(message, possible_cities)
		else:
			logger.error(f'Ошибка запроса. код ошибки {response_city.status_code} user_id {message.chat.id}')
			bot.send_message(message.chat.id, f'Ошибка запроса. код ошибки {response_city.status_code}')
			bot.send_message(message.chat.id, 'Выполните команду еще раз и введите город.')


@bot.message_handler(state=HotelInfoState.count_hotels)
def get_count_hotels(message: Message) -> None:
	"""
	Ввод пользователем кол-во отелей для вывода.
	Проверка входил ли это число в диапазон от 1 до 25.
	:param message: Message
	:return: None
	"""
	if message.text.isdigit():
		if 0 < int(message.text) < 25:
			logger.info(f'Ввод пользователем и запись количества отелей в поиске '
						f' {message.text} User_id {message.chat.id}')
			with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
				data['count_hotels'] = message.text
				bot.set_state(message.chat.id, HotelInfoState.min_price)
				bot.send_message(message.chat.id, 'Введите минимальную стоимость за сутки в отеле в долларах (США):')
		else:
			bot.send_message(message.chat.id, 'Число не может быть меньше 0 и больше 25')
	else:
		bot.send_message(message.chat.id, 'Ошибка, вы ввели не число!')


@bot.message_handler(state=HotelInfoState.min_price)
def get_min_price(message: Message) -> None:
	"""
	Ввод минимальной стоимости отеля и проверка ввода на число.
	:param message: Message
	:return: None
	"""
	if message.text.isdigit():
		if int(message.text) > 0:
			logger.info(f'Ввод пользователем и запись минимальной цены за отель '
						f'{message.text} User_id {message.chat.id}')
			with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
				data['min_price'] = message.text
				bot.set_state(message.from_user.id, HotelInfoState.max_price, message.chat.id)
				bot.send_message(message.chat.id, 'Введите максимальную стоимость за сутки в отеле в долларах (США)')
		else:
			bot.send_message(message.chat.id, 'Стоимость не может быть меньше нуля')
	else:
		bot.send_message(message.chat.id, 'Может содержать только цифры')


@bot.message_handler(state=HotelInfoState.max_price)
def get_max_price(message: Message) -> None:
	"""
	Ввод максимальной стоимости отеля и проверка ввода на число.
	Вызов и создание кнопок о необходимости фотографий отеля.
	:param message: Message
	:return: None
	"""
	if message.text.isdigit():
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			if int(data['min_price']) < int(message.text):
				logger.info(f'Ввод пользователем и запись максимальной цены за отель '
							f'{message.text} User_id {message.chat.id}')
				data["max_price"] = message.text
				create_buttons.need_for_photo(message)
			else:
				bot.send_message(message.chat.id, 'Максимальная цена не может быть меньше минимальной')
	else:
		bot.send_message('Может содержать только цифры')


@bot.message_handler(state=HotelInfoState.count_photo)
def get_count_photo(message: Message) -> None:
	"""
	Ввод пользователем кол-во фотографий и проверка ввода на число.
	Вызов и создания кнопок с календарем с датой заезда
	:param message: Message
	:return: None
	"""
	if message.text.isdigit():
		if 0 < int(message.text) <= 10:
			logger.info(f'Ввод пользователем и запись количества фотографий'
						f' {message.text} User_id {message.chat.id}')
			with bot.retrieve_data(message.chat.id) as data:
				data['count_photo'] = int(message.text)
			my_calendar(message, 'заезда')
		else:
			bot.send_message(message.chat.id, 'Фотографий не может быть меньше 0 или больше 10')
	else:
		bot.send_message(message.chat.id, 'Ошибка ввода. Нужно ввести число')


@bot.message_handler(state=HotelInfoState.min_distance_to_center)
def min_distance_to_center(message: Message) -> None:
	"""
	Ввод пользователем минимального расстояния отеля до центра.
	Проверка ввода на число
	:param message: Message
	:return: None
	"""
	if message.text.isdigit():
		logger.info(f'Ввод пользователем минимальное расстояние до центра '
					f'{message.text} User_id {message.chat.id}')
		with bot.retrieve_data(message.chat.id) as data:
			data['min_distance'] = message.text
			bot.set_state(message.from_user.id, HotelInfoState.max_distance_to_center, message.chat.id)
			bot.send_message(message.chat.id, 'Пожалуйста введите максимальное расстояние отеля до центра (Км)')
	else:
		bot.send_message(message.chat.id, 'Ошибка. Нужно ввести число')


@bot.message_handler(state=HotelInfoState.max_distance_to_center)
def min_distance_to_center(message: Message) -> None:
	"""
	Ввод пользователем максимального расстояния отеля до центра.
	Проверка ввода на число
	:param message: Message
	:return: None
	"""
	if message.text.isdigit():
		logger.info(f'Ввод пользователем максимальное расстояние до центра {message.text} User_id {message.chat.id}')
		with bot.retrieve_data(message.chat.id) as data:
			data['max_distance'] = message.text
			add_to_bd.add_query(data)
			find_hotel(message, data)
	else:
		bot.send_message(message.chat.id, 'Ошибка. Нужно ввести число')


bot_calendar = Calendar()


def my_calendar(message, word):
	"""
	Создание календаря и вывод его в бота
	:param message: Message
	:param word: str заезда/выезда
	:return: None
	"""
	logger.info(f'Вызов календаря {word} User_id {message.chat.id}')
	bot.send_message(message.chat.id, f'Выберете дату {word}', reply_markup=bot_calendar.create_calendar())


def check_command(command: str) -> str:
	"""
	Проверка команды и назначение параметра сортировки
	: param command : str команда, выбранная (введенная) пользователем
	: return : str команда сортировки
	"""
	if command == '/custom':
		return 'DISTANCE'
	elif command == '/lower' or command == '/high':
		return 'PRICE_LOW_TO_HIGH'