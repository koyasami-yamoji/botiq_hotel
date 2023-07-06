from loader import bot
from loguru import logger
from states.hotel_information import HotelInfoState
from handlers.custom_handlers.custom import my_calendar


@bot.callback_query_handler(func=lambda call: call.data.isalpha())
def need_photo_callback(call) -> None:
	"""
	Пользователь нажал кнопку "Да" или "Нет" на клавиатуре с вопрос о необходимости фотографий.
	:param call: "Да" или "Нет"
	:return: None
	"""
	if call.data == 'да':
		logger.info(f'Пользователь нажал "да" user_id {call.message.chat.id}')
		with bot.retrieve_data(call.message.chat.id) as data:
			data['need_photo'] = call.data
		bot.delete_message(call.message.chat.id, call.message.message_id)
		bot.set_state(call.message.chat.id, HotelInfoState.count_photo)
		bot.send_message(call.message.chat.id, 'Введите количество фотографий (не больше 10)')
	elif call.data == 'нет':
		logger.info(f'Пользователь нажал "нет" user_id {call.message.chat.id}')
		with bot.retrieve_data(call.message.chat.id) as data:
			data['need_photo'] = call.data
			data['count_photo'] = 0
			bot.delete_message(call.message.chat.id, call.message.message_id)
			my_calendar(call.message, 'заезда')
