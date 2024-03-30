FROM python:3.8-buster

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY main.py ./
COPY src /app/src
CMD python main.py