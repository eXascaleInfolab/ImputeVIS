FROM node:14

# Setup frontend environment
RUN mkdir /app
WORKDIR /app
ADD ./parameterizer_frontend/package*.json /app/
RUN npm install

# Add install and startup scripts
ADD ./install_linux.sh /install_linux.sh
ADD ./start_servers.sh /start_frontend.sh

# Grant execution permissions
RUN chmod +x /install_linux.sh /start_frontend.sh

# Run the installation script
RUN /install_linux.sh

CMD ["/start_frontend.sh"]
