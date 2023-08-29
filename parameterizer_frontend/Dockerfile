FROM node:18

# Setup frontend environment
RUN mkdir /app
WORKDIR /app

# Since Dockerfile is inside 'parameterizer_frontend', just refer directly to the files
# ADD ./package*.json /app/
# Brute-force adding all files that may be required
ADD ./*.json /app/
ADD ./*.ts /app/

RUN npm install && npm i vite

# Add the startup script.
ADD ./start_frontend.sh /start_frontend.sh

# Grant execution permissions
RUN chmod +x /start_frontend.sh
