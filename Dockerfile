FROM python:3.8-slim as backend
WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH=/src

VOLUME /src/logs

COPY src .
