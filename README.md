# msc_thesis_timeseries

Repository for my Master Thesis' code base, that is under the [eXascale](https://exascale.info/) institute at University of Fribourg, Switzerland.

The thesis on the general topic of Timeseries and focuses on:
- Python Implementation of the IIM (Individual Imputation Model)
- Implementing the shared information metric
- Parametrizing algorithms timeseries recovery algorithms, based on the category: matrix-based, pattern-based, neural-network-based, and regression-based.
- Using a GUI that shows the effects of the different parameters on the different types of algorithms and their output for reconstruction.
- Possible characterizing datasets
- Possibly suggesting optimal parameters and best algorithms.

## Stack
- Vue.js with Vite and Typescript for the front-end.
- Django 4 for the back-end.

## Prerequisites
- Node.js and npm (npm is distributed with Node.js - which means that when you download Node.js, you automatically get npm installed on your computer)
- Python (version 3.8 or later) and pip
- Vue CLI
- Django 4

## Installation
### Frontend
Navigate to the frontend directory.
```bash
cd parameterizer_frontend
```

Install dependencies using npm.
```bash
npm install
```

To start the development server.
```bash
npm run dev
```

### Backend
Navigate to the backend directory.
```bash
cd timeSeriesImputerParameterizer
```

Create a virtual environment and activate it.
```bash
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

Install Django and other dependencies.
```bash
pip install -r requirements.txt
```

To start the development server.
```bash
python manage.py runserver
```

## Usage
After setting up the frontend and backend, you can access the application by opening http://localhost:5173 in your browser.

## Contributing
Might be possible after the thesis has finished, but currently this is not desired.

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
