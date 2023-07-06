import requests
from config_data import config


headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": config.RAPID_API_KEY,
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def api_request(method_type: str = None, url: str = None, params: dict = None):
	"""
	Отправка запроса на сервер
	:param method_type:  str
	:param url:  str
	:param params: dict
	:return: None
	"""
	if method_type == 'GET':
		response_get = requests.get(url=url, params=params, headers=headers)
		return response_get
	elif method_type == 'POST':
		response_post = requests.post(url=url, json=params, headers=headers)
		return response_post