#!/bin/bash
# Unused, but kept for reference

# Start Backend Server
echo "Starting backend server..."

cd timeSeriesImputerParameterizer
source env/bin/activate
python manage.py runserver &

# Give some time for the backend server to initialize
sleep 5

# Start Frontend Server
echo "Starting frontend server..."

cd ../parameterizer_frontend
npm run dev &

# Navigate back to the root directory
cd ..

echo "Backend and frontend servers are now running!"

# Note: Both servers are started in the background using '&'. This will allow you to continue
# using the terminal. If you want to stop the servers, you can find their process IDs using 'ps'
# and then 'kill' the processes.
