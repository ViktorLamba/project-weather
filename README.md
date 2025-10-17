# 🌤️ Weather App

Простое веб-приложение для просмотра погоды в различных городах мира, построенное на Flask и Open-Meteo API.

## 🚀 Функциональность

- 🔍 **Поиск погоды** по названию города
- 🌍 **Поддержка популярных городов** (Москва, Лондон, Париж, Токио, Нью-Йорк и другие)
- 📱 **Адаптивный дизайн** для мобильных устройств
- ⚡ **Быстрый доступ** к погоде через предустановленные кнопки


📊 Данные о погоде
Приложение использует Open-Meteo API для получения актуальных данных о погоде:

Текущая температура

Минимальная/максимальная температура

Скорость ветра

Описание погодных условий

Географические координаты


## 🛠️ Технологии

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS
- **API**: Open-Meteo API для получения данных о погоде

## 📦 Установка и запуск

## Установка

1. **Клонируйте репозиторий**:
```bash
git clone <URL-репозитория>
cd Project-weather

### Создание виртуального окружения (Linux)

$ python -m venv venv
$ source venv/bin/activate

### Установка зависимосткей

$ pip install -r requirements.txt 

##🏗️ Структура проекта
Project-weather/
│
├── app/
│ ├── client
│ │ ├── static/
│ │ │ │ ├── css/
│ │ │ │ ├── images/
│ │ │ │ └── js/
│ │ └── templates/
│ │     ├── base.html
│ │     ├── index.html
│ │     └── weather.html
│ └── weather/
│      ├── init.py
│      └── controller.py # Нахождение погоды (back)
│ 
│
├── venv/
├── .gitignore
├── main.py # Точка входа
├── README.md
└── requirements.txt


##📞 Контакты
git - https://github.com/ViktorLamba
tg - @viiiii_tyok