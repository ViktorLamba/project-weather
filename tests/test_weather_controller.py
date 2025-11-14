import pytest
from unittest.mock import patch, MagicMock
from app.weather.controller import weather, get_weather_description, get_weather_main
from flask import Flask


@pytest.fixture
def client():
    app = Flask(
        __name__,
        template_folder="app/client/templates",
        static_folder="app/client/static"
    )
    app.register_blueprint(weather)
    app.config["TESTING"] = True
    return app.test_client()


# TEST /weather-page
def test_weather_page(client, mocker):
    # Мокаем render_template в том модуле, где он используется
    mock_render = mocker.patch('app.weather.controller.render_template')
    mock_render.return_value = '<html>Mocked template</html>'

    response = client.get("/weather-page?city=Moscow")
    assert response.status_code == 200

    mock_render.assert_called_once()
    mock_render.assert_called_with('weather.html', city='Moscow', lat=None, lon=None)


# TEST /weather — invalid coords
def test_get_weather_invalid_coords(client):
    resp = client.get("/weather?lat=999&lon=10")
    data = resp.json

    assert resp.status_code == 400
    assert data["status"] == 1
    assert data["error"] == "Неверные координаты"


# TEST /weather by coordinates
@patch("app.weather.controller.get_weather_from_openmeteo")
@patch("app.weather.controller.get_city_name")
@patch("app.weather.controller.db_engine")
def test_get_weather_by_coords(mock_db, mock_city, mock_weather, client):
    """Проверяем корректный сценарий по координатам."""

    mock_city.return_value = "Москва"

    mock_weather.return_value = {
        "current_temp": 10,
        "weather_code": 2,
        "weather_description": "Облачно",
        "wind_speed": 3.5,
        "max_temp": 12,
        "min_temp": 8
    }

    mock_conn = MagicMock()
    mock_db.connect.return_value.__enter__.return_value = mock_conn

    resp = client.get("/weather?lat=55.75&lon=37.62")
    data = resp.json

    assert resp.status_code == 200
    assert data["status"] == 0
    assert data["data"]["name"] == "Москва"
    assert data["data"]["main"]["temp"] == 10
    assert mock_conn.execute.called


# TEST /weather by city name
@patch("app.weather.controller.find_city_coordinates")
@patch("app.weather.controller.get_weather_from_openmeteo")
@patch("app.weather.controller.db_engine")
def test_get_weather_by_city(mock_db, mock_weather, mock_coords, client):

    mock_coords.return_value = (50.0, 30.0)

    mock_weather.return_value = {
        "current_temp": 5,
        "weather_code": 0,
        "weather_description": "Ясно",
        "wind_speed": 1.0,
        "max_temp": 7,
        "min_temp": 3
    }

    mock_conn = MagicMock()
    mock_db.connect.return_value.__enter__.return_value = mock_conn

    resp = client.get("/weather?city=Moscow")
    data = resp.json

    assert resp.status_code == 200
    assert data["status"] == 0
    assert data["data"]["coord"]["lat"] == 50.0
    assert data["data"]["weather"][0]["description"] == "Ясно"


# TEST: city not found
@patch("app.weather.controller.find_city_coordinates")
def test_city_not_found(mock_coords, client):
    mock_coords.return_value = None

    resp = client.get("/weather?city=Atlantida")
    data = resp.json

    assert resp.status_code == 400
    assert data["status"] == 1
    assert "не найден" in data["error"]


# TEST: get_weather_description
def test_get_weather_description():
    assert get_weather_description(0) == "Ясно"
    assert get_weather_description(95) == "Гроза"
    assert get_weather_description(999) == "Неизвестно"


# TEST: get_weather_main
def test_get_weather_main():
    assert get_weather_main(0) == "Clear"
    assert get_weather_main(61) == "Rain"
    assert get_weather_main(999) == "Clouds"
