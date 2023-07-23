#!/bin/bash
# TODO Does not work, use Docker instead
echo "Activating virtual environment:"
source env/bin/activate

echo "Starting backend server..."
cd timeSeriesImputerParameterizer

python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
