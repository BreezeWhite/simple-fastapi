
import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from celery.result import AsyncResult

from .celery_server import app as cel_app, add, check_task_in_queue
from .models import AddData


app = FastAPI()

# This is the default logger that used by Gunicorn server.
# We have also added customized handlers to this logger.
# Please refer to `Makefile` and `logger.py` for more details.
logger = logging.getLogger("gunicorn.error")


@app.get("/")
async def root():
    return {"message": "Hello FastAPI~"}


@app.post("/submit/add", tags=['Addition'])
async def submit_add(a: float, b: float):
    logger.info("User submitted a task to addition")
    task = add.delay(a, b)
    return {"Task ID": task.id}


@app.get("/result/add/{task_id}", response_description="", tags=["Addition"])
async def get_add_result(task_id: str):
    logger.info("Requested task ID: %s", task_id)

    task = AsyncResult(task_id, app=cel_app)
    if not task.ready():
        if await check_task_in_queue(task_id):
            # To avoid 'TypeError: NetworkError', add '--http0.9' flag to the curl command.
            logger.info("Requested task not ready. Task ID: %s", task_id)
            return JSONResponse({"Message": "Task pending or not exists."}, status_code=status.HTTP_102_PROCESSING)
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Task not found with the given ID: {task_id}")

    if task.successful():
        logger.info("Task succeeded: %s", task_id)
        return {"Result": task.get()}
