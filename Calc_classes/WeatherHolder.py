import requests
from datetime import datetime


# Класс обработки погоды
class WeatherHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/"

    def get_weather_data(self, city):
        """Основной метод для получения всех данных о погоде"""
        try:
            # Получаем текущую погоду
            current_url = f"{self.base_url}weather?q={city}&appid={self.api_key}&units=metric&lang=ru"
            current_res = requests.get(current_url)
            current_res.raise_for_status()

            # Получаем прогноз
            forecast_url = f"{self.base_url}forecast?q={city}&appid={self.api_key}&units=metric&lang=ru"
            forecast_res = requests.get(forecast_url)
            forecast_res.raise_for_status()

            return {
                'current': self._parse_current(current_res.json()),
                'forecast': self._parse_forecast(forecast_res.json())
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError("Город не найден")
            raise Exception(f"Ошибка API: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка: {str(e)}")

    def _parse_current(self, data):
        """Парсинг данных текущей погоды"""
        return {
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'description': data['weather'][0]['description'].capitalize(),
            'time': datetime.fromtimestamp(data['dt']).strftime('%H:%M')
        }

    def _parse_forecast(self, data):
        """Парсинг данных прогноза"""
        forecast = []
        for item in data['list'][:3]:  # Берем первые 3 интервала
            forecast.append({
                'temp': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'description': item['weather'][0]['description'].capitalize(),
                'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M')
            })
        return forecast