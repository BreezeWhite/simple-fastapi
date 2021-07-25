import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from celery.exceptions import SoftTimeLimitExceeded

from .celery_server import app as cel_app, add, is_prime, check_task_in_queue


app = FastAPI()

# This is the default logger that used by Gunicorn server.
# We have also added customized handlers to this logger.
# Please refer to `Makefile` and `logger.py` for more details.
logger = logging.getLogger("gunicorn.error")


#########################################
## Start to define your endpoints here ##
#########################################

@app.get("/")
async def root():
    return {"message": "Hello FastAPI~"}


# ------------- Addition ------------- #
@app.post("/submit/add", status_code=status.HTTP_201_CREATED, tags=['Addition'])
async def submit_add(a: float, b: float):
    logger.info("User submitted a task to addition")
    task = add.delay(a, b)
    return {"Task ID": task.id}


@app.get("/result/add/{task_id}", response_description="Returns the addition result", tags=["Addition"])
async def get_add_result(task_id: str):
    result = await common_get_result_handler(task_id)
    return {"Result": result}


# ------------- Is Prime ------------- #
@app.post("/submit/isPrime", status_code=status.HTTP_201_CREATED, tags=["Prime"])
async def submit_is_prime(num: int):
    logger.info("User submitted a task to is_prime")
    task = is_prime.delay(num)
    return {"Task ID": task.id}


@app.get(
    "/result/isPrime/{task_id}",
    response_description="Returns whether the number is prime or not",
    tags=["Prime"]
)
async def get_prime_result(task_id: str):
    isp = await common_get_result_handler(task_id)
    if isp:
        return {"Message": "It's prime"}
    return {"Message": "The number is not prime"}


#################################################
## Below are some convenient utility functions ##
#################################################

async def common_get_result_handler(task_id: str):
    logger.info("Requested task ID: %s", task_id)

    task = AsyncResult(task_id, app=cel_app)
    ready, resp = await check_ready_state(task, task_id)
    if not ready:
        return resp

    if task.successful():
        logger.info("Task succeeded: %s", task_id)
        return task.get()

    await check_common_failure(task)


async def check_common_failure(task):
    try:
        task.get()
    except SoftTimeLimitExceeded:
        logger.warn("Task excution time exceeded the soft limit: \n%s", task.traceback)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Process time exceeded the soft limit.")


async def check_ready_state(task, task_id):
    if not task.ready():
        if await check_task_in_queue(task_id):
            # To avoid 'TypeError: NetworkError', add '--http0.9' flag to the curl command.
            logger.info("Requested task not ready. Task ID: %s", task_id)
            return False, JSONResponse({"Message": "Task pending or not exists."}, status_code=status.HTTP_102_PROCESSING)
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Task not found with the given ID: {task_id}")
    return True, None
