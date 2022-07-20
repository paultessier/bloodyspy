FROM python:3.8-slim-buster
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
# RUN /usr/local/bin/python -m pip install --upgrade pip
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD uvicorn app:api --host 0.0.0.0 --port 8000
