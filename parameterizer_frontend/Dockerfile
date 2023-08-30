FROM node:18

# Setup frontend environment
RUN mkdir /app
WORKDIR /app

# Since Dockerfile is inside 'parameterizer_frontend', just refer directly to the files
# ADD ./package*.json /app/
# Brute-force adding all files that may be required
COPY ./*.json ./*.ts /app/

# Install dependencies
RUN npm install

# The CMD will execute when the container starts and will run the frontend server
CMD ["npm", "run", "dev-host"]
