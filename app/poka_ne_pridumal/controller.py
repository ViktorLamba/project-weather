"""Simple Flask application to find cities using OpenWeatherMap API."""
from flask import Blueprint


weather = Blueprint('weather', __name__)


@weather.route('/find-city', methods=['GET'])
def find_city(s_city):
    pass
