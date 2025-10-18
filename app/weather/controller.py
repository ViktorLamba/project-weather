"""Получение погоды."""
from flask import Blueprint, jsonify, request, render_template
import requests
from sqlalchemy import create_engine, text

weather = Blueprint('weather', __name__)

db_engine = create_engine("postgresql://user:1@localhost:5432/postgres")

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
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    return render_template('weather.html', city=city, lat=lat, lon=lon)


@weather.route('/weather', methods=['GET'])
def get_weather():
    """Получение погоды для заданного города или координат."""
    try:
        city_name = request.args.get('city')
        lat = request.args.get('lat')
        lon = request.args.get('lon')

        if lat and lon:
            try:
                lat_float = float(lat)
                lon_float = float(lon)

                if not (-90 <= lat_float <= 90) or not (-180 <= lon_float <= 180):
                    return jsonify({'status': 1, 'error': 'Неверные координаты'}), 400

                weather_data = get_weather_from_openmeteo(lat_float, lon_float)

                city_name_from_coords = get_city_name(lat_float, lon_float)

                formatted_data = {
                    'name': city_name_from_coords,
                    'sys': {'country': 'N/A'},
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
                        'lat': lat_float,
                        'lon': lon_float
                    }
                }
                try:
                    with db_engine.connect() as conn:
                        conn.execute(text("""
                        INSERT INTO weather_data(city_name, lat, lon, weather, temp, max_temp, min_temp, wind, humidity)
                        VALUES (:city_name, :lat, :lon, :weather, :temp, :max_temp, :min_temp, :wind, :humidity)
                        """).bindparams(city_name=city_name_from_coords,
                                        lat=lat_float,
                                        lon=lon_float,
                                        weather=weather_data['weather_description'],
                                        temp=weather_data['current_temp'],
                                        max_temp=weather_data['max_temp'],
                                        min_temp=weather_data['min_temp'],
                                        wind=weather_data['wind_speed'],
                                        humidity=65))
                        conn.commit()
                except Exception as e:
                    return jsonify({f'status': 1, 'error': f'Ошибка подключения к базе данных:{e}'}), 500

                return jsonify({'status': 0, 'data': formatted_data})

            except ValueError:
                return jsonify({'status': 1, 'error': 'Координаты должны быть числами'}), 400

        # Если передан город, ищем по названию
        elif city_name and city_name != 'None':
            city_coords = find_city_coordinates(city_name)
            if not city_coords:
                return jsonify({'status': 1, 'error': f'Город "{city_name}" не найден'}), 404

            weather_data = get_weather_from_openmeteo(city_coords['lat'],
                                                      city_coords['lon'])

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

            try:
                with db_engine.connect() as conn:
                    conn.execute(text("""
                    INSERT INTO weather_data(city_name, lat, lon, weather, temp, max_temp, min_temp, wind, humidity)
                    VALUES (:city_name, :lat, :lon, :weather, :temp, :max_temp, :min_temp, :wind, :humidity)
                    """).bindparams(city_name=city_coords['name'],
                                    lat=city_coords['lat'],
                                    lon=city_coords['lon'],
                                    weather=weather_data['weather_description'],
                                    temp=weather_data['current_temp'],
                                    max_temp=weather_data['max_temp'],
                                    min_temp=weather_data['min_temp'],
                                    wind=weather_data['wind_speed'],
                                    humidity=65))
                    conn.commit()

            except Exception as e:
                return jsonify({'status': 1, 'error': f'Ошибка подключения к базе данных: {e}'}), 500

            return jsonify({'status': 0, 'data': formatted_data})

        else:
            return jsonify({'status': 1, 'error': 'Укажите название города или координаты'}), 400

    except Exception as e:
        return jsonify({'status': 1, 'error': str(e)}), 500


def find_city_coordinates(s_city):
    """Поиск координат города по названию."""
    if not s_city or s_city == 'None':
        return None

    city_lower = s_city.lower().strip()

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


def get_city_name(lat, lon):
    """Получение названия города по координатам."""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'accept-language': 'ru',
            'addressdetails': 1,
            'zoom': 10
        }

        # Добавляем правильные заголовки для Nominatim
        headers = {
            'User-Agent': 'WeatherApp/1.0 (your-email@example.com)',
            'Accept': 'application/json'
        }

        response = requests.get(url,
                                params=params,
                                headers=headers,
                                timeout=10)

        response.raise_for_status()
        data = response.json()

        if data.get('address'):
            address = data['address']

            # Ищем название города в разных полях
            city_name = (
                address.get('city') or
                address.get('town') or
                address.get('village') or
                address.get('municipality') or
                address.get('county') or
                address.get('state') or
                address.get('region')
            )

            if city_name:
                return city_name

        # Если город не найден, возвращаем координаты
        result = f"Координаты ({lat:.2f}, {lon:.2f})"
        return result

    except Exception:
        result = f"Координаты ({lat:.2f}, {lon:.2f})"
        return result


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
