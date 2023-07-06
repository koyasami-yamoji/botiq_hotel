from dataclasses import dataclass
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import calendar
import datetime


@dataclass
class Language:
	days: tuple
	months: dict


RUSSIAN_LANGUAGE = Language(
	days=("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"),
	months={
		'January': "Январь",
		'February': "Февраль",
		'March': "Март",
		'April': "Апрель",
		'May': "Май",
		'June': "Июнь",
		'July': "Июль",
		'August': "Август",
		'September': "Сентябрь",
		'October': "Октябрь",
		'November': "Ноябрь",
		'December': "Декабрь"
		}
)


class Calendar:
	__lang = Language

	def __init__(self, language: Language = RUSSIAN_LANGUAGE):
		self.__lang = language

	def create_calendar(self, year=None, month=None):
		now_date = datetime.datetime.now()

		if year is None:
			year = now_date.year
		if month is None:
			month = now_date.month

		date_ignore = CallbackData.create_callback_data('IGNORE', year, month, 0)

		keyboard = []
		row = [InlineKeyboardButton(self.__lang.months[calendar.month_name[month]] + " " + str(year),
									callback_data=date_ignore)]
		keyboard.append(row)

		row = []
		for day in self.__lang.days:
			row.append(InlineKeyboardButton(day, callback_data=date_ignore))
		keyboard.append(row)

		my_calendar = calendar.monthcalendar(year, month)
		for week in my_calendar:
			row = []
			for day in week:
				if day == 0:
					row.append(InlineKeyboardButton(' ', callback_data=date_ignore))
				else:
					row.append(InlineKeyboardButton(day, callback_data=CallbackData.create_callback_data(
						'DAY', year, month, day)))
			keyboard.append(row)

		row = [InlineKeyboardButton('<--', callback_data=f'PREV-MONTH;{year};{month}'),
			   InlineKeyboardButton(' ', callback_data=date_ignore),
			   InlineKeyboardButton('-->', callback_data=f'NEXT-MONTH;{year};{month}')]

		keyboard.append(row)

		return InlineKeyboardMarkup(keyboard)

	def calendar_query_handler(self, bot, call, action, year, month, day):
		(action, year, month, day) = (action, year, month, day)
		current_data = datetime.datetime(int(year), int(month), 1)
		if action == 'IGNORE':
			bot.answer_callback_query(callback_query_id=call.id)
			return False, None

		elif action == "DAY":
			return None

		elif action == 'PREV-MONTH':
			prev_month = current_data - datetime.timedelta(days=1)
			bot.edit_message_text(text=call.message.text,
								  chat_id=call.message.chat.id,
								  message_id=call.message.message_id,
								  reply_markup=self.create_calendar(int(prev_month.year), int(prev_month.month)))
			return None

		elif action == 'NEXT-MONTH':
			next_month = current_data + datetime.timedelta(days=31)
			bot.edit_message_text(text=call.message.text,
								  chat_id=call.message.chat.id,
								  message_id=call.message.message_id,
								  reply_markup=self.create_calendar(int(next_month.year), int(next_month.month)))
			return None

		else:
			bot.answer_callback_query(callback_query_id=call.id, text='Что-то пошло не так')
			bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
			return None


class CallbackData:

	@staticmethod
	def create_callback_data(action, year, month, day):
		return ';'.join([action, str(year), str(month), str(day)])

	@staticmethod
	def separate_data(data):
		return data.split(';')


def check_month_day(number: str) -> str:
	"""
	Преобразование формата числа месяца или дня из формата 1..9 в формат 01..09
	: param number : str, число месяца или дня
	: return number : str
	"""
	numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	if int(number) in numbers:
		number = '0' + number
	return number