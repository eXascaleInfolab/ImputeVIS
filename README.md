# ImputeVIS

The repository was built within the [eXascale](https://exascale.info/) group at the University of Fribourg, Switzerland.


## Prerequisites

- Ubuntu 20 or Ubuntu 22 (including Ubuntu derivatives, e.g., Xubuntu) or the same distribution under WSL2
- Updated version of Docker
- Clone this repository.



## Quick Start Linux (and Mac)
Install or update docker and docker-compose. Then run the following commands:

```bash
# Build images
docker-compose build  
# Start images
docker-compose up
```

Then navigate into the `parameterizer_frontend` directory, make sure that npm is installed, and run the following commands:

```bash
npm install
npm run dev
```

This uses the docker-compose.yml file to build the frontend and backend and run them in containers.   
The front end is available at http://localhost:5173 (or http://172.19.0.3:5173/),
and the back end is accessible under http://localhost:8000 (API calls only).


## Quick Start Windows
Install or update docker for Windows under WSL, then run the following commands:

```bash
# Build backend image
docker-compose build backend
# Start backend image
docker-compose up backend
```

Then navigate into the `parameterizer_frontend` directory, make sure that npm is installed, and run the following commands:

```bash
npm install
npm run dev
```

## Usage

After setting up the frontend and backend, you can access the application by opening http://localhost:5173 in your
browser.


## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
