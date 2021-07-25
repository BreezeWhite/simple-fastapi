# Simple FastAPI Template

A simple, minimum, ready-to-go FastAPI template that could be setup in just a few minutes. Coordinates with Celery for distributed workload in the backend. Suitable for heavy computational scenarios such as machine learning, image processing, audio processing, etc.

It's easy to extend and implement more tasks. Just add tasks in `src/celery_server.py` and also the corresponding endpoints to `src/server.py`, then it's all done. No additional configurations are required.

# Quick start
``` bash
# Clone this repo
git clone https://github.com/BreezeWhite/simple-fastapi.git

# Install dependencies
make install

# Start serving
make start
```
You can access and test the API from the browser. Just enter `http://127.0.0.1:8001/docs`.


## Docker
Dockerfile is also provided for convenience. To build the image, run the following command:
```bash
make build-docker
```

And to run the built image, execute following commnad:
```bash
docker run -it --rm \
    -p 8001:8001 \
    -p 5672:5672 \
    -p 4369:4369 \
    -p 15672:15672 \
    simple-fastapi:latest
```

## Advanced

### Distributed workload

Usually, the picture looks like this:
```
Request --> Endpoint --(register task)--> Broker --(dispatch task)--> Worker
            <FastAPI>                   <RabbitMQ>                   <Celery>
```
All three serivces run on a single machine.

But with Celery, you can deploy multiple workers accross different machines to increase the computation power.
```
                          ------> Worker (Machine 1)
                          |
Request --> Endpoint --> Broker ---> Worker (Machine 2)
                          |
                          ------> worker (Machine 3)
```
To do this, first launch the endpoint server and broker service on the same machine:
```bash
# It's neccessary to have a account registered to RabbitMQ for Celery to
# login when Celery is running on a different machine.
export RABBIT_NAME=bonny
export RABBIT_PWD=love-carrot
make register-rabbit

# (Optional) To make the endpoint available from anywhere, change the binding IP as following.
export GUNICORN_SERVE_URL=0.0.0.0:8001

# Start the endpoint server
make start-gunicorn
```
After launching the above services, you can now launch the Celery on different machines
and all connect to the same broker.
```bash
# Fill in the account information you've just setup.
export CELERY_BROKER_HOST=<ip address of the broker>
export CELERY_BROKER_USER=bonny
export CELERY_BROKER_PASSWORD=love-carrot

# To run in foreground
make start-celery-stdout

# To run in background
make start-celery
```
Congratulations! You've just finished setup an distributed backend services!