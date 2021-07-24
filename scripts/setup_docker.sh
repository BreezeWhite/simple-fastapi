#!/bin/bash

# Manually setup docker to run on an Ubuntu machine.

sudo apt update
sudo apt install docker.io python3-pip
sudo groupadd docker
sudo usermod -aG docker $USER

# Logout and login again
pip install --upgrade pip
export CELERY_BROKER_HOST=localhost
export GUNICORN_SERVE_URL=0.0.0.0:8001

docker run -it --rm \
    -p 8001:8001 \
    -p 5672:5672 \
    -p 4369:4369 \
    -p 15672:15672 \
    -e GUNICORN_SERVE_URL \
    -e CELERY_BROKER_HOST \
    simple-fastapi:latest bash