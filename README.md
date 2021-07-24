# Simple FastAPI Template

A simple, minimum, ready-to-go FastAPI template that could be setup in just a few minutes. Coordinates with Celery for distributed workload in the backend. Suitable for heavy computational scenarios such as machine learning, image processing, audio processing, etc.

It's easy to extend and implement more tasks. Just add tasks in `src/celery_server.py` and also the corresponding endpoints to `src/server.py`, then it's all done. No additional configurations are required.

# Quick start
``` bash
# Clone this repo
git clone https://github.com/BreezeWhite/simple-fastapi.git

# Install dependencies
make init

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
To be continued...