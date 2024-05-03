# https://docs.streamlit.io/deploy/tutorials/docker

# Docker image
FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    build-essential curl software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Allow statements and log messages to immediately appear in logs
ENV PYTHONUNBUFFERED True

# run and add virtual env in PATH
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# set the container's working directory
WORKDIR /app

# copy requirements file and install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy all of the app files to the working directory
COPY . .

EXPOSE $PORT

# https://docs.docker.com/reference/dockerfile/#healthcheck
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health

# command to run the streamlit app
CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0