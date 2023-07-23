#!/bin/bash

echo "Starting backend server..."
apt update
apt install -y libopenblas-dev
cd /app
source env/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
