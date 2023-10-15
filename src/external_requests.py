import requests # Использование httpx или aiohttp для асинхронности 


WEATHER_API_KEY = '99ba78ee79a2a24bc507362c5288a81b' # Добавить в виртуальное окружение .env load_dotenv()


class GetWeatherRequest():
    """
    Выполняет запрос на получение текущей погоды для города
    """

    def __init__(self):
        """
        Инициализирует класс
        """
        self.session = requests.Session()
        # Инициализировать WEATHER_API_KEY тут же

    def get_weather_url(self, city): # Использование params из requests для создания url
        # base_url = 'https://api.openweathermap.org/data/2.5/weather'
        # params = {
        #     'units': 'metric',
        #     'q': 'city',
        #     'appid': 'WEATHER_API_KEY'
        # }
        # return base_url, params
        """
        Генерирует url включая в него необходимые параметры
        Args:
            city: Город # Указывать тип первым str
        Returns:
            str: Сформированный URL для запроса погоды
        """
        url = 'https://api.openweathermap.org/data/2.5/weather'
        url += '?units=metric'
        url += '&q=' + city
        url += '&appid=' + WEATHER_API_KEY
        return url

    def send_request(self, url):
        """
        Отправляет запрос на сервер
        Args:
            url: Адрес запроса
        Returns:
            requests.Response: Объект ответа от сервера
        """
        # r = self.session.get(base_url, params=params)
        r = self.session.get(url)
        if r.status_code != 200:
            r.raise_for_status()
        return r

    def get_weather_from_response(self, response):
        """
        Достает погоду из ответа
        Args:
            response: Ответ, пришедший с сервера
        Returns:
            float or None: Температура в градусах Цельсия или None, если что-то пошло не так
        """
        data = response.json()
        return data['main']['temp'] # Обернуть в try для случаев когда город не существует

    def get_weather(self, city):
        """
        Делает запрос на получение погоды
        Args:
            city: Город
        Returns:
            float or None: Температура в градусах Цельсия или None, если что-то пошло не так
        """
        url = self.get_weather_url(city)
        r = self.send_request(url) 
        if r is None: # requests всегда вернет объект и мы можем проверить его статус и более явно выявлять ошибки if r.status_code == 200
            return None
        else:
            weather = self.get_weather_from_response(r)
            return weather


class CheckCityExisting():
    """
    Проверка наличия города (запросом к серверу погоды)
    """

    def __init__(self):
        """
        Инициализирует класс
        """
        self.session = requests.Session()

    def get_weather_url(self, city): # Использование params из requests для создания url
        """
        Генерирует url включая в него необходимые параметры
        Args:
            city: Город
        Returns:
            str: Сформированный URL для запроса погоды
        """
        url = 'https://api.openweathermap.org/data/2.5/weather'
        url += '?units=metric'
        url += '&q=' + city
        url += '&appid=' + WEATHER_API_KEY
        return url

    def send_request(self, url):
        """
        Отправляет запрос на сервер
        Args:
            url: Адрес запроса
        Returns:
            requests.Response: Объект ответа от сервера
        """
        
        r = self.session.get(url)
        return r

    def check_existing(self, city):
        """
        Проверяет наличие города
        Args:
            city: Название города
        Returns:
            bool: True, если город существует, False в противном случае
        """
        url = self.get_weather_url(city)
        r = self.send_request(url) # не сокращать наименования r = response
        if r.status_code == 404: # Использование raise_for_status()
            return False
        if r.status_code == 200:
            return True
