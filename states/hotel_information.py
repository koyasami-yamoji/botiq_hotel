from telebot.handler_backends import State, StatesGroup


class HotelInfoState(StatesGroup):
	input_command = State()
	city = State()
	count_days = State()
	min_distance_to_center = State()
	max_distance_to_center = State()
	count_photo = State()
	date = State()
	max_price = State()
	min_price = State()
	count_hotels = State()
	input_date = State()
	select_number = State()