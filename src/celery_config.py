""" Config file for celery.
Extensive configuration options can be found in the following page:
https://docs.celeryproject.org/en/stable/userguide/configuration.html
"""
import os

CELERY_BROKER_USER = os.environ.get("CELERY_BROKER_USER", "guest")
CELERY_BROKER_PASSWORD = os.environ.get("CELERY_BROKER_PASSWORD", None)
CELERY_BROKER_HOST = os.environ.get("CELERY_BROKER_HOST", "localhost")
CELERY_BROKER_TYPE = 'amqp://'

if CELERY_BROKER_PASSWORD is not None:
    broker_url = f'{CELERY_BROKER_TYPE}{CELERY_BROKER_USER}:{CELERY_BROKER_PASSWORD}@{CELERY_BROKER_HOST}:5672/'
else:
    broker_url = f'{CELERY_BROKER_TYPE}{CELERY_BROKER_USER}@{CELERY_BROKER_HOST}:5672/'


# Default result backend is to use RabbitMQ.
result_backend = 'rpc://'

# Send task events to event monitor. Execute 'celery events' to monitor.
worker_send_task_events = True

# 5 mins, will raise SoftTimeLimitExceeded exception
task_soft_time_limit = 300

# Hard time limit, will not raise any exception
task_time_limit = 360

# Expire the result after seconds
result_expires = 3600
