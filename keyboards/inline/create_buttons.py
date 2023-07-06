from loader import bot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger


def need_for_photo(message) -> None:
	"""
	Создание кнопок о необходимости фотографий отеля
	:param message: Message
	:return: None
	"""
	logger.info(f'Вывод кнопок о необходимости фотографий пользователю user_id {message.chat.id}')
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton(text='Да', callback_data='да'),
				 InlineKeyboardButton(text='Нет', callback_data='нет'))
	bot.send_message(message.chat.id, 'Нужны ли фотографии отеля?', reply_markup=keyboard)


def show_cities_buttons(message, possible_cities) -> None:
	"""
	Создание кнопок с возможными городами из запроса пользователя.
	:param message: Message
	:param possible_cities: Dict полученные города с запроса на сервер
	:return: None
	"""
	logger.info(f'Вывод кнопок возможных городов User_id: {message.chat.id}')
	keyboard_cities = InlineKeyboardMarkup()
	for key, value in possible_cities.items():
		keyboard_cities.add(InlineKeyboardButton(text=value['regionNames'], callback_data=value['gaiaId']))
	bot.send_message(message.chat.id, 'Выберете город', reply_markup=keyboard_cities)