# msc_thesis_timeseries

Repository for my Master Thesis' code base, that is under the [eXascale](https://exascale.info/) institute at University
of Fribourg, Switzerland.

The thesis on the general topic of Timeseries and focuses on:

- Python Implementation of the IIM (Individual Imputation Model)
- Implementing the shared information metric
- Parametrizing algorithms timeseries recovery algorithms, based on the category: matrix-based, pattern-based,
  neural-network-based, and regression-based.
- Using a GUI that shows the effects of the different parameters on the different types of algorithms and their output
  for reconstruction.
- Possible characterizing datasets
- Possibly suggesting optimal parameters and best algorithms.

## Quick Start Linux (and Mac)
Install docker and docker-compose. Then run the following commands:

```bash
# Build images
docker-compose build  
# Start images
docker-compose up
```
This uses the docker-compose.yml file to build the frontend and backend and run them in containers.   
The frontend is available at http://localhost:5173 (or http://172.19.0.3:5173/), 
with the backend accessible under http://localhost:8000 (api calls only).

## Quick Start Windows
Install docker for windows under WSL, then run the following commands:

```bash
# Build backend image
docker-compose build backend
# Start backend image
docker-compose up backend
```

Either in Windows directly or under WSL, install npm if not already installed.
Then navigate into the `parameterizer_frontend` directory, make sure that npm is installed, and run the following commands:

```bash
npm install
npm run dev
```

## Prerequisites

- Ubuntu 20 or Ubuntu 22 (including Ubuntu derivatives, e.g., Xubuntu) or the same distribution under WSL2
- Clone this repository.
- `install_linux.sh` and `start_servers.sh` should suffice (untested).

Alternatively dependencies if doing it manually:

- Node.js and npm (npm is distributed with Node.js) for the frontend dependencies in `package.json`.
- Python (version 3.8 or later) and pip.
- Django 4 (installed via pip with requirements.txt).

## Manual Installation

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

#### WSL (Minimum for Backend if not on Linux)

Navigate to directory in which project has been cloned and into the server, e.g.:

```bash
cd d/Git/msc_thesis_timeseries/timeSeriesImputerParameterizer/parameterizer/
```

And then run the following command:

```bash
python manage.py runserver
```

Furthermore, the following dependency may be needed for WSL:

```bash
sudo apt-get install libopenblas-dev
```

### Troubleshooting
**Docker won't work for the frontend**
You are likely under Windows, using WSL2 for Docker.  
"@esbuild/win32-x64" does not have the same binaries as "@esbuild/linux-x64",
thus either start the frontend manually with `npm install` and `npm run dev` in the `parameterizer_frontend` directory,
or manually navigate under your WSL2 installation to the `parameterizer_frontend` directory, install node within your WSL,
and run `npm install`. Ensure that the node version used is the Linux and not Windows one.  
After this, the issue should likely be fixed for `docker-compose up frontend`.

**The frontend shows errors and won't start**
Ensure you are using `npm run dev` to start the frontend and not attempting to run `npm run build`.

## Usage

After setting up the frontend and backend, you can access the application by opening http://localhost:5173 in your
browser.

## Contributing

Might be possible after the thesis has finished, but currently this is not desired.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
