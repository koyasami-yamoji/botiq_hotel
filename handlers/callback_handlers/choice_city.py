from loader import bot
from loguru import logger
from states import hotel_information


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def choice_city(call) -> None:
	"""
	Обработчик нажатия пользователем на кнопку с возможными городами из запроса.
	:param call: Выбранный город
	:return: None
	"""
	logger.info(f'Пользователь выбрал город. User_id {call.message.chat.id} Id Города {call.data}')
	if call.data:
		with bot.retrieve_data(call.message.chat.id) as data:
			data['destination_id'] = call.data
			bot.delete_message(call.message.chat.id, call.message.message_id)
			bot.set_state(call.message.chat.id, hotel_information.HotelInfoState.count_hotels)
			bot.send_message(call.message.chat.id, 'Сколько отелей вывести в чат? (не больше 25)')