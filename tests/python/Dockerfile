FROM python:3.8-slim-buster
RUN apt-get update
# RUN apt-get install ffmpeg libsm6 libxext6  -y
WORKDIR /app
ADD test_api.py test_api.py
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir log data
# EXPOSE 8000
CMD python3 test_api.py
