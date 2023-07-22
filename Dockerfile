FROM python:3.8

# Set up environment
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD timeSeriesImputerParameterizer/requirements.txt /app/

# Update and install essential packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils && \
    apt-get install -y libopenblas-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python requirements
RUN pip install -r requirements.txt

# Add the start_backend.sh script to the Docker image
ADD start_backend.sh /start_backend.sh

# Make sure the start_backend.sh script is executable
RUN chmod +x /start_backend.sh

CMD ["/start_backend.sh"]
