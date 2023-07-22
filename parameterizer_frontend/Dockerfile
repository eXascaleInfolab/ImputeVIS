FROM node:18

# Setup frontend environment
RUN mkdir /app
WORKDIR /app

# Since Dockerfile is inside 'parameterizer_frontend', just refer directly to the files
ADD ./package*.json /app/
RUN npm install && npm i vite

# Add the startup script. I removed the install_linux.sh as it seems redundant in this context.
ADD ./start_frontend.sh /start_frontend.sh

# Grant execution permissions
RUN chmod +x /start_frontend.sh
