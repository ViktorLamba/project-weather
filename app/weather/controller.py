"""Simple Flask application to find cities using Open-Meteo API."""
from flask import Blueprint, jsonify, request, render_template
import requests

weather = Blueprint('weather', __name__)

# Координаты популярных городов
CITY_COORDINATES = {
    'moscow': {'lat': 55.7558, 'lon': 37.6173, 'name': 'Москва', 'country': 'RU'},
    'london': {'lat': 51.5074, 'lon': -0.1278, 'name': 'Лондон', 'country': 'GB'},
    'paris': {'lat': 48.8566, 'lon': 2.3522, 'name': 'Париж', 'country': 'FR'},
    'berlin': {'lat': 52.5200, 'lon': 13.4050, 'name': 'Берлин', 'country': 'DE'},
    'tokyo': {'lat': 35.6762, 'lon': 139.6503, 'name': 'Токио', 'country': 'JP'},
    'new york': {'lat': 40.7128, 'lon': -74.0060, 'name': 'Нью-Йорк', 'country': 'US'},
    'petersburg': {'lat': 59.9311, 'lon': 30.3609, 'name': 'Санкт-Петербург', 'country': 'RU'},
    'sochi': {'lat': 43.5855, 'lon': 39.7231, 'name': 'Сочи', 'country': 'RU'},
    'kazan': {'lat': 55.7961, 'lon': 49.1064, 'name': 'Казань', 'country': 'RU'}
}


@weather.route('/weather-page', methods=['GET'])
def weather_page():
    """Страница с фронтендом для просмотра погоды."""
    city = request.args.get('city', 'Moscow')
    return render_template('weather.html', city=city)  


@weather.route('/weather', methods=['GET'])
def get_weather():
    """Получение погоды для заданного города."""
    try:
        city_name = request.args.get('city', 'Moscow')
        
        # Получаем координаты города
        city_coords = find_city_coordinates(city_name)
        if not city_coords:
            return jsonify({'status': 1, 'error': f'Город "{city_name}" не найден'}), 404
        
        # Получаем погоду
        weather_data = get_weather_from_openmeteo(city_coords['lat'], city_coords['lon'])
        
        formatted_data = {
            'name': city_coords['name'],
            'sys': {'country': city_coords['country']},
            'main': {
                'temp': weather_data['current_temp'],
                'feels_like': weather_data['current_temp'],
                'temp_min': weather_data['min_temp'],
                'temp_max': weather_data['max_temp'],
                'humidity': 65
            },
            'weather': [{
                'description': weather_data['weather_description'],
                'main': get_weather_main(weather_data['weather_code'])
            }],
            'wind': {
                'speed': weather_data['wind_speed']
            },
            'coord': {
                'lat': city_coords['lat'],
                'lon': city_coords['lon']
            }
        }

        return jsonify({'status': 0, 'data': formatted_data}), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({'status': 1, 'error': str(e)}), 500


def find_city_coordinates(s_city):
    """Поиск координат города по названию."""
    city_lower = s_city.lower().strip()

    # Ищем названия городов
    for city_key, coords in CITY_COORDINATES.items():
        if city_lower in city_key or city_key in city_lower:
            return coords

    return None


def get_weather_from_openmeteo(lat, lon):
    """Получение погоды от Open-Meteo API."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,weather_code,wind_speed_10m',
            'daily': 'temperature_2m_max,temperature_2m_min,weather_code',
            'timezone': 'auto',
            'forecast_days': 1
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        current = data['current']
        daily = data['daily']

        weather_code = current['weather_code']

        return {
            'current_temp': current['temperature_2m'],
            'weather_code': weather_code,
            'weather_description': get_weather_description(weather_code),
            'wind_speed': current['wind_speed_10m'],
            'max_temp': daily['temperature_2m_max'][0],
            'min_temp': daily['temperature_2m_min'][0]
        }

    except Exception as e:
        raise Exception(f'Ошибка получения погоды: {str(e)}')


def get_weather_description(code):
    """Преобразуем код погоды в описание на русском."""
    weather_descriptions = {
        0: 'Ясно',
        1: 'Преимущественно ясно',
        2: 'Переменная облачность',
        3: 'Пасмурно',
        45: 'Туман',
        48: 'Туман с инеем',
        51: 'Легкая морось',
        53: 'Умеренная морось',
        55: 'Сильная морось',
        61: 'Небольшой дождь',
        63: 'Умеренный дождь',
        65: 'Сильный дождь',
        80: 'Ливень',
        95: 'Гроза'
    }
    return weather_descriptions.get(code, 'Неизвестно')


def get_weather_main(code):
    """Преобразуем код погоды в основную категорию."""
    weather_mapping = {
        0: 'Clear',
        1: 'Clear',
        2: 'Clouds',
        3: 'Clouds',
        45: 'Fog',
        48: 'Fog',
        51: 'Rain',
        53: 'Rain',
        55: 'Rain',
        61: 'Rain',
        63: 'Rain',
        65: 'Rain',
        80: 'Rain',
        95: 'Thunderstorm'
    }
    return weather_mapping.get(code, 'Clouds')