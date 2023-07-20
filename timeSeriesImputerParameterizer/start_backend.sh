#!/bin/bash

echo "Starting backend server..."
cd /app
source env/bin/activate
python manage.py runserver 0.0.0.0:8000
