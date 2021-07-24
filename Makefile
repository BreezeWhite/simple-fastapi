# Parameter settings
# All the following paramters can be overwritten by exporting
# environment variables with the same name

# Celery parameters
CELERY_SERVER_LOG_FILE ?= logs/celery.log
CELERY_BROKER_USER ?=
CELERY_BROKER_PASSWORD ?=
CELERY_BROKER_HOST ?=

# Gunicorn parameters
GUNICORN_WORKERS ?= 1
GUNICORN_LOG_PATH ?= logs/gunicorn-daily-log
GUNICORN_ACCESS_LOG_FILE ?= logs/gunicorn-access.log
GUNICORN_SERVE_URL ?= 127.0.0.1:8001  # Change to 0.0.0.0:8001 to serve requests from anywhere.


# RabbitMQ (the default broker type) parameters
RABBIT_NAME ?= bonny
RABBIT_PWD ?= love-carrot

###############################
## End of parameter settings ##
###############################

###############################
## Post-configure parameters ##
###############################


# Check if current user is root.
ifneq ($(shell id -u), 0)
SUDO = sudo
endif

# Setup environment variables for Celery server
ifeq ($(CELERY_BROKER_HOST),)
start-celery-stdout: export CELERY_BROKER_HOST = localhost
start-celery-stdout: export CELERY_BROKER_USER = guest
start-celery: export CELERY_BROKER_HOST = localhost
start-celery: export CELERY_BROKER_USER = guest
else
	ifeq ($(CELERY_BROKER_PASSWORD),)
start-celery-stdout: export CELERY_BROKER_PASSWORD = ${RABBIT_PWD}
start-celery: export CELERY_BROKER_PASSWORD = ${RABBIT_PWD}
	endif
	ifeq ($(CELERY_BROKER_USER),)
start-celery-stdout: export CELERY_BROKER_USER = ${RABBIT_NAME}
start-celery: export CELERY_BROKER_USER = ${RABBIT_NAME}
	endif
endif

# Setup environment variables for Gunicorn(FastAPI) server
ifeq ($(GUNICORN_LOG_PATH),)
start-gunicorn: export GUNICORN_LOG_PATH = logs/gunicorn-daily-log
endif


########################
## Executable targets ##
########################

init: install register-rabbit
start: start-rabbit start-celery start-gunicorn
restart: stop-celery start-celery start-gunicorn
stop: stop-celery stop-rabbit

install:
	$(SUDO) apt-get update && $(SUDO) apt-get --yes install \
		rabbitmq-server \
		make \
		python3=3.8.2-0ubuntu2 \
		python3-pip
	pip install --upgrade pip
	pip install wheel
	pip install -r requirements.txt

start-rabbit:
	$(SUDO) rabbitmq-server -detached &> /dev/null && echo "Node online" || echo "Already running"
	sleep 5

register-rabbit: start-rabbit
	$(SUDO) rabbitmqctl add_user ${RABBIT_NAME} ${RABBIT_PWD}
	$(SUDO) rabbitmqctl add_vhost /
	$(SUDO) rabbitmqctl set_user_tags ${RABBIT_NAME} admin
	$(SUDO) rabbitmqctl set_permissions -p / ${RABBIT_NAME} ".*" ".*" ".*"

start-gunicorn:
	gunicorn src.server:app \
		--bind ${GUNICORN_SERVE_URL} \
		--workers ${GUNICORN_WORKERS} \
		--worker-class uvicorn.workers.UvicornWorker \
		--access-logfile ${GUNICORN_ACCESS_LOG_FILE} \
		--logger-class src.logger.MyLogger

start-celery-stdout:
	celery -A src.celery_server:app worker \
		--loglevel=INFO \
		--task-events

start-celery:
	celery -A src.celery_server:app worker \
		--loglevel=INFO \
		-f ${CELERY_SERVER_LOG_FILE} \
		--task-events \
		--detach

stop-celery:
	celery control shutdown || echo "Shutdown"

stop-rabbit:
	$(SUDO) rabbitmqctl shutdown

build-docker:
	docker build --network=host -t simple-fastapi .
