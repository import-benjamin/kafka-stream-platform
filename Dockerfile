FROM python:3.8-buster

LABEL Name "Python producer" DESCRIPTION "Easy API to produce message to kafka"

RUN pip3 install confluent_kafka flask
WORKDIR /home/api

ENTRYPOINT [ "flask", "run", "--host", "0.0.0.0"]