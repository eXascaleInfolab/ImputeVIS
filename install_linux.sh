#!/bin/bash
# Unused, but kept for reference
# Check for Ubuntu 20, 22 or WSL2
#if ! (lsb_release -a 2>/dev/null | grep -E "Ubuntu 20|Ubuntu 22" || grep -q Microsoft /proc/version); then
#    echo "Unsupported system! This script is for Ubuntu 20, Ubuntu 22, and WSL2 with Ubuntu."
#    exit 1
#fi

# Install prerequisites
echo "Installing prerequisites..."

sudo apt update
sudo apt install -y libopenblas-dev nodejs npm python3.8 python3-pip python3-venv

# Check for Node.js and npm
if ! (node -v && npm -v) > /dev/null; then
    echo "Error: Node.js and npm are required!"
    exit 1
fi

# Frontend installation
echo "Installing frontend dependencies..."
cd parameterizer_frontend
npm install

# To start the frontend development server, uncomment the line below
# npm run dev

# Navigate back to root directory
cd ..

# Backend installation
echo "Setting up backend environment..."
cd timeSeriesImputerParameterizer

# Extract the Python 3 minor version number
PYTHON3_MINOR_VERSION=$(python3 --version | awk '{print $2}' | cut -d'.' -f2)

# Install the appropriate venv module
sudo apt install -y python3.${PYTHON3_MINOR_VERSION}-venv

# Create virtual environment (if not already created)
if [ ! -d "env" ]; then
    python3 -m venv env
    source env/bin/activate
fi

# Install Django and other dependencies
pip install -r requirements.txt

# To start the backend development server, uncomment the line below
# python manage.py runserver

echo "Installation complete!"

# Note: The 'npm run dev' and 'python manage.py runserver' commands are commented out,
# so they won't be executed by the script.
# You can uncomment them if you want the servers to start right after the installation.
# If you do so, you will need to open a new terminal window to run the other command.
