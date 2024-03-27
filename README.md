# ImputeVIS

Repository built within the the [eXascale](https://exascale.info/) institute at University of Fribourg, Switzerland.


## Prerequisites

- Ubuntu 20 or Ubuntu 22 (including Ubuntu derivatives, e.g., Xubuntu) or the same distribution under WSL2
- Clone this repository.

## Dependencies:

- Node.js and npm (npm is distributed with Node.js) for the frontend dependencies in `package.json`.
- Python (version 3.8 or later) and pip.
- Django 4 (installed via pip with requirements.txt).


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

## Usage

After setting up the frontend and backend, you can access the application by opening http://localhost:5173 in your
browser.

## Contributing

Might be possible after the thesis has finished, but currently this is not desired.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
