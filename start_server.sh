#!/bin/sh
. venv/bin/activate
gunicorn -b 127.0.0.1:$PORT -b [::1]:$PORT -w 1 --max-requests 500 --max-requests-jitter 50 yr:app