# TODO This does not work yet
FROM python:3.8-slim

# Set up environment
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r requirements.txt

# Add install and startup scripts
#ADD ../install_linux.sh /install_linux.sh
#ADD ../start_servers.sh /start_backend.sh

# Grant execution permissions
#RUN chmod +x /install_linux.sh /start_backend.sh

# Run the installation script
#RUN /install_linux.sh

# Make sure the start_backend.sh script is executable
RUN chmod +x /app/start_backend.sh

CMD ["/app/start_backend.sh"]
