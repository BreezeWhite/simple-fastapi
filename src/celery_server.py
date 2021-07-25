import time
import math

from celery import Celery
from celery.utils.log import get_task_logger
from celery.signals import task_prerun


app = Celery('celery-server')
app.config_from_object('src.celery_config')
logger = get_task_logger(__name__)


################################
## Define your own tasks here ##
################################

@app.task
def health_check():
    return "I'm fine, thank you, and you?"


@app.task
def add(a, b):
    time.sleep(15)
    return a + b


@app.task
def is_prime(num: int) -> bool:
    if num <= 1:
        return False
    if num == 2:
        return True

    scan_range = math.ceil(pow(num, 0.5)) + 1
    for div in range(2, scan_range):
        if num % div == 0:
            return False
    return True


#####################
## Other utilities ##
#####################

@task_prerun.connect
def prerun_handler(task_id, task, **kwargs):
    # Change the default 'PENDING' status to 'SENT' of a published task for 
    # later distinguishing between submitted and non-exists task ID.
    task.backend.store_result(task_id=task_id, result=None, state="SENT")


async def check_task_in_queue(task_id):
    # Check if the given task ID is in queue.
    if app.backend.get_status(task_id) == "SENT":
        # The state is set to 'SENT' before running.
        return True

    # Not yet running but is in queue.
    stats = app.control.inspect().reserved()
    for tlist in stats.values():
        for task in tlist:
            if task['id'] == task_id:
                return True
    return False


def main():
    # For health check
    result = health_check.delay()
    while not result.ready():
        pass
    return result.get()


if __name__ == "__main__":
    main()
