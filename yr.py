import threading
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template

from weather_data import WeatherData


app = Flask(__name__)


CACHE_TIME = timedelta(minutes=20)

_create_weather_data_instance_lock = threading.RLock()
_weather_data = (None, None)


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.
    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }
    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        server = environ.get('HTTP_X_FORWARDED_SERVER', '')
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)


app.wsgi_app = ReverseProxied(app.wsgi_app)


@app.route("/")
def weather():
    weather_data = get_weather_data()
    relative_time = weather_data.get_time()
    symbol = weather_data.get_symbol()
    temperature = weather_data.get_temperature()
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

        if weather_data is None or current_time() > expires_at:
            weather_data = WeatherData()
            weather_data.populate()
            _weather_data = (weather_data, current_time() + CACHE_TIME)
        return weather_data


def current_time():
    return datetime.now(timezone.utc)
