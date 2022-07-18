FROM python:3.8-slim-buster
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
# RUN /usr/local/bin/python -m pip install --upgrade pip
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD uvicorn app:api --port 8000
# CMD ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "8000"]


# FROM ubuntu:20.04
# RUN apt update && apt install python3-pip libmysqlclient-dev
# WORKDIR /app
# COPY requirements.txt requirements.txt
# RUN pip install -r requirements.txt
# COPY . .
# EXPOSE 8000
# CMD uvicorn app:server --host 0.0.0.0


# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
# WORKDIR /app
# COPY . .

# FROM python:3.7
# RUN pip install fastapi uvicorn
# EXPOSE 80
# COPY ./app /app
# CMD ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "80"]


# FROM debian:latest
# RUN apt-get update && apt-get install python3-pip -y
# ADD tests_content.py /my_server/tests_content.py
# ADD requirements.txt /my_server/requirements.txt
# WORKDIR /my_server/
# RUN pip3 install -r requirements.txt
# RUN mkdir log
# EXPOSE 8000
# CMD python3 tests_content.py
