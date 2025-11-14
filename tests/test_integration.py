import json
from unittest.mock import Mock


class TestIntegration:
    """Интеграционные тесты."""

    def test_full_weather_flow_city(self, client, mock_requests, mock_db_engine):
        """Полный тест потока получения погоды по городу."""
        mock_engine, mock_conn = mock_db_engine

        mock_geocoding = Mock()
        mock_geocoding.json.return_value = {
            'results': [{'latitude': 55.7558, 'longitude': 37.6173}]
        }

        mock_weather = Mock()
        mock_weather.json.return_value = {
            'current': {
                'temperature_2m': 15.5,
                'weather_code': 0,
                'wind_speed_10m': 3.2
            },
            'daily': {
                'temperature_2m_max': [18.0],
                'temperature_2m_min': [12.0]
            }
        }

        mock_requests.get.side_effect = [mock_geocoding, mock_weather]

        response = client.get('/weather?city=Moscow')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['status'] == 0
        assert data['data']['name'] == 'Moscow'
        assert data['data']['main']['temp'] == 15.5
        assert data['data']['main']['temp_max'] == 18.0
        assert data['data']['main']['temp_min'] == 12.0
        assert data['data']['weather'][0]['description'] == 'Ясно'
        assert data['data']['weather'][0]['main'] == 'Clear'

        mock_conn.execute.assert_called()

    def test_full_weather_flow_coordinates(self, client, mock_requests, mock_db_engine):
        """Полный тест потока получения погоды по координатам."""
        mock_engine, mock_conn = mock_db_engine

        mock_weather = Mock()
        mock_weather.json.return_value = {
            'current': {
                'temperature_2m': 20.0,
                'weather_code': 1,
                'wind_speed_10m': 5.0
            },
            'daily': {
                'temperature_2m_max': [22.0],
                'temperature_2m_min': [18.0]
            }
        }

        mock_reverse = Mock()
        mock_reverse.json.return_value = {
            'address': {'city': 'Saint Petersburg'}
        }

        mock_requests.get.side_effect = [mock_weather, mock_reverse]

        response = client.get('/weather?lat=59.9343&lon=30.3351')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['status'] == 0
        assert data['data']['name'] == 'Saint Petersburg'
        assert data['data']['coord']['lat'] == 59.9343
        assert data['data']['coord']['lon'] == 30.3351

        mock_conn.execute.assert_called()
