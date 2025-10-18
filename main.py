"""Точка входа для приложения Flask."""
from flask import Flask, render_template
from app.weather.controller import weather

app = Flask(__name__,
            template_folder='app/client/templates',  # ← путь к шаблонам
            static_folder='app/client/static')

app.register_blueprint(weather)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
