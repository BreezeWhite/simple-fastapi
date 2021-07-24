FROM ubuntu:20.04

COPY src /app/src
COPY Makefile /app
COPY Dockerfile /app
COPY requirements.txt /app

WORKDIR /app
RUN mkdir logs
RUN apt-get --yes update && apt-get --yes install make
RUN make install

CMD make start