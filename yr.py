import threading
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template

from weather_data import WeatherData


app = Flask(__name__)


CACHE_TIME = timedelta(minutes=20)

_create_weather_data_instance_lock = threading.RLock()
_weather_data = (None, None)


@app.route("/")
def weather():
    weather_data = get_weather_data()
    relative_time = weather_data.get_time()
    symbol = weather_data.get_symbol()
    temperature = weather_data.get_symbol()
    return render_template(
        "yr.html",
        time=relative_time,
        symbol=symbol,
        temperature=temperature,
    )



def get_weather_data():
    global _weather_data
    with _create_weather_data_instance_lock:
        weather_data, expires_at = _weather_data
        weather_data_is_expired = current_time() > expires_at

        if weather_data is None or weather_data_is_expired:
            weather_data = WeatherData()
            weather_data.populate()
            _weather_data = (weather_data, current_time() + CACHE_TIME)
        return weather_data


def current_time():
    return datetime.now(timezone.utc)
