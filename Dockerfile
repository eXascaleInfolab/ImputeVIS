FROM python:3.8-slim

# Set up environment
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD ./timeSeriesImputerParameterizer/requirements.txt /app/
RUN pip install -r requirements.txt

# Add install and startup scripts
ADD ./install_linux.sh /install_linux.sh
ADD ./start_servers.sh /start_backend.sh

# Grant execution permissions
RUN chmod +x /install_linux.sh /start_backend.sh

# Run the installation script
RUN /install_linux.sh

CMD ["/start_backend.sh"]
