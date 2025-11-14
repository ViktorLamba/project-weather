import pytest
from unittest.mock import Mock, patch
from flask import Flask
import sys
import os

from app.weather.controller import weather

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app():
    """Создает тестовое приложение Flask."""
    app = Flask(__name__)
    app.config['TESTING'] = True

    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/client/templates'))
    app.template_folder = template_dir

    app.register_blueprint(weather)
    return app


@pytest.fixture
def client(app):
    """Создает тестовый клиент."""
    return app.test_client()


@pytest.fixture
def mock_requests():
    """Мок для requests."""
    with patch('app.weather.controller.requests') as mock_requests:
        yield mock_requests


@pytest.fixture
def mock_db_engine():
    """Мок для базы данных."""
    with patch('app.weather.controller.db_engine') as mock_engine:
        mock_conn = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        yield mock_engine, mock_conn


@pytest.fixture
def sample_weather_data():
    """Пример данных о погоде."""
    return {
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


@pytest.fixture
def sample_geocoding_data():
    """Пример данных геокодинга."""
    return {
        'results': [
            {
                'latitude': 55.7558,
                'longitude': 37.6173,
                'name': 'Moscow'
            }
        ]
    }


@pytest.fixture(autouse=True)
def mock_render_template():
    """Автоматически мокаем render_template для всех тестов."""
    with patch('app.weather.controller.render_template') as mock_render:
        mock_render.return_value = "<html>Mocked template</html>"
        yield mock_render
