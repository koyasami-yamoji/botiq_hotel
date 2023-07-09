from loader import bot
from loguru import logger
import datetime
from database import add_to_bd
from utils.find_hotel import find_hotel
from handlers.custom_handlers.custom import my_calendar
from keyboards.calendar.create_calendar import Calendar, check_month_day
from states.hotel_information import HotelInfoState

calendar = Calendar()


@bot.callback_query_handler(func=lambda call: call.data.startswith('DAY') or call.data.startswith('PREV-MONTH') or
											  call.data.startswith('NEXT-MONTH'))
def input_date(call):
	"""
	Обработчик нажатия пользователем на кнопки календаря.
	Вызов ввода минимального расстояния.
	:param call: Выбор дня/Прошлый/Следующий месяц
	:return: None
	"""
	print(call.data)
	try:
		action, year, month, day = call.data.split(';')
	except ValueError:
		action, year, month = call.data.split(';')
		day = datetime.datetime.now().day

	calendar.calendar_query_handler(bot=bot, call=call, action=action, year=year, month=month, day=day)

	if action == 'DAY':
		bot.set_state(call.message.chat.id, HotelInfoState.input_date)
		logger.info(f'Выбрана дата пользователем, проверяем User_id: {call.message.chat.id}')
		select_date = year + check_month_day(month) + check_month_day(day)

		with bot.retrieve_data(call.message.chat.id) as data:
			if 'checkInDate' in data:
				checkin = int(data['checkInDate']['year'] + data['checkInDate']['month'] + data['checkInDate']['day'])

				if int(select_date) > checkin:
					logger.info(f'Ввод и сохранения даты выезда пользователем {call.message.chat.id}')
					data['checkOutDate'] = {'day': day, 'month': month, 'year': year}

					data['min_distance'] = 0
					data['max_distance'] = 0
					bot.delete_message(call.message.chat.id, call.message.message_id)

					if data['sort'] == 'DISTANCE':
						bot.set_state(call.message.chat.id, HotelInfoState.min_distance_to_center)
						bot.send_message(call.message.chat.id,
										 'Введите максимальное значение расстояния отеля до центра (Км)')
					else:
						add_to_bd.add_query(data)
						find_hotel(call, data)

				else:
					bot.send_message(call.message.chat.id, 'Дата выезда должна быть больше даты заезда, '
														   'Повторите выбор')
					bot.delete_message(call.message.chat.id, call.message.message_id)
					my_calendar(call.message, word='выезда')

			else:
				logger.info(f'Ввод и сохранения даты заезда пользователем User_id {call.message.chat.id}')
				data['checkInDate'] = {'day': day, 'month': month, 'year': year}
				bot.delete_message(call.message.chat.id, call.message.message_id)
				my_calendar(call.message, word='выезда')

