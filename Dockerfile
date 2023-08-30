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

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
