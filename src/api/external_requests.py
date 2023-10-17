import os
import logging

# Использование httpx или aiohttp для асинхронности при увеличении числа пользователей
import requests

from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger("uvicorn")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


class WeatherBase:
    """
    Базовый классс для работы с Open Weather Map
    """
        
    def get_params(self, city):
        """
        Собирает необходимые данные для запроса
        Args:
            str: City
        Returns:
            url: str + params: Dict[str: str]
        """
        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'units': 'metric',
            'q': city,
            'appid': WEATHER_API_KEY
        }
        return url, params

    def send_request(self, url, params):
        """
        Запрос
        Args:
            url: str + params: Dict[str: str]
        Returns:
            response или None в случае ошибки
        """
        try:
            with requests.get(url, params=params) as response:
                response.raise_for_status()
                return response
        except requests.exceptions.RequestException as e:
            city = params.get('q')
            logger.error(f"Error fetching weather for {city}: {e}")
            return None


class GetWeatherRequest(WeatherBase):
    """
    Выполняет запрос на получение текущей температуры для города
    """
    def get_weather(self, city):
        """
        Делает запрос на получение погоды
        Args:
            str: City
        Returns:
            float or None: Температура в градусах Цельсия или None, если что-то пошло не так
        """
        if not isinstance(city, str):
            raise ValueError("City must be a string.")

        url, params = self.get_params(city)

        response = self.send_request(url, params)
        if response is None:
            return None
        
        weather = response.json()
        temp = weather.get('main', {}).get('temp')
        if temp is None:
            return None
        return float(temp)


class CheckCityExisting(WeatherBase):
    def check_existing(self, city):
        """
        Проверяет наличие города
        Args:
            city: Название города
        Returns:
            bool: True, если город существует, False в противном случае
        """
        url, params = self.get_params(city)
        response = self.send_request(url, params)
        if response is None:
            return False
        return response.status_code == 200
