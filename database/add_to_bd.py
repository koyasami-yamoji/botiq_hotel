import sqlite3
from config_data import config
from telebot.types import Message
from loguru import logger


def add_user(message: Message) -> None:
	"""
	Создает базу данных если ее еще нет.
	Создает таблицу с данными пользователя.
	Не используется для выдачи информации.
	Нужна только для хранения данных.
	:param message: Message
	:return: None
	"""
	connection = sqlite3.connect(config.DB_NAME)
	cursor = connection.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
				chat_id INTEGER UNIQUE NOT NULL,
				username TEXT NOT NULL);
				""")
	connection.commit()
	try:
		cursor.execute("SELECT INTO user(chat_id, username) VALUES (?, ?)",
					   (message.chat.id, message.from_user.username))
		logger.info(f'Добавлен новый пользователь. User_id {message.chat.id}')
		connection.commit()
	except sqlite3.IntegrityError:
		logger.info(f'Данный пользователь уже существует. {message.chat.id}')
	connection.close()


def add_query(query_data: dict) -> None:
	"""
	Создает таблицу если она еще не создана и добавляет туда данные запроса,
	которые ввел пользователь для поиска.
	:param query_data: dict
	:return: None
	"""
	user_id = query_data['chat_id']
	connection = sqlite3.connect(config.DB_NAME)
	cursor = connection.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS query(
	       id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	       user_id INTEGER,
	       date_time STRING, 
	       city STRING,
	       destination_id STRING,
	       photo_need STRING,
	       response_id INTEGER,
	       FOREIGN KEY (response_id) REFERENCES response(id) ON DELETE CASCADE ON UPDATE CASCADE
	   );    
	   """)
	connection.commit()
	try:
		logger.info(f'Добавление в базу данных нового запроса User_id {user_id}')
		cursor.execute("""INSERT INTO query(user_id, date_time, city, destination_id) VALUES(?, ?, ?, ?)""", (
			user_id,
			query_data['date_time'],
			query_data['city'],
			query_data['destination_id'],
		))
		cursor.execute(f"""
		                DELETE FROM query WHERE query.[date_time]=
		                (SELECT MIN([date_time]) FROM query WHERE `user_id` = '{user_id}' )
		                AND
		                ((SELECT COUNT(*) FROM query WHERE `user_id` = '{user_id}' ) > 5 ) 
		            """)
		connection.commit()
	except sqlite3.IntegrityError:
		logger.info(f'Запрос с такой датой уже существует')
	connection.close()


def add_response(search_result: dict) -> None:
	"""
	Создает таблицу если она еще не создана и добавляет туда данные отеля,
	которые бот получил от сервера.
	:param search_result:
	:return: None
	"""
	connection = sqlite3.connect(config.DB_NAME)
	cursor = connection.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS response(
					id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
					hotel_id STRING,
					name STRING,
					address STRING,
					price REAL,
					distance REAL,
					 FOREIGN KEY (hotel_id) REFERENCES images(hotel_id) ON DELETE CASCADE ON UPDATE CASCADE
					 );
					 """)

	for item in search_result.items():
		cursor.execute(f"SELECT 'id' FROM query WHERE 'date_time' = ?", (item[1]['date_time'],))
		cursor.execute("INSERT INTO response(hotel_id, name, address, price, distance)"
					   " VALUES (?, ?, ?, ?, ?)",
					   (
						   item[0],
						   item[1]['name'],
						   item[1]['address'],
						   item[1]['price'],
						   item[1]['distance']
					   ))
		logger.info(f'В БД добавлены данные отеля {item[0]}. User_id: {item[1]["user_id"]}')
		if item[1]['images']:
			for url in item[1]['images']:
				cursor.execute("""CREATE TABLE IF NOT EXISTS images(
								id INTEGER PRIMARY KEY AUTOINCREMENT,
								hotel_id INTEGER REFERENCES response (id),
								url TEXT
								);""")
				cursor.execute("INSERT INTO images (hotel_id, url) VALUES (?, ?)", (item[0], url))
			logger.info(f'В ДБ добавлены ссылки на фотографии отеля {item[0]}. User_id {item[1]["user_id"]}')
			connection.commit()
		connection.close()






