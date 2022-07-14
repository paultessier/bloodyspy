# FROM python:3.8
FROM python:3.8-slim-buster
# RUN apt-get update && apt-get install libgl1
# RUN apt-get update
# RUN apt-get install ffmpeg libsm6 libxext6  -y
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
# CMD streamlit run app.py --server.port 8000 --logger.level=debug 2> streamlit_logs.log
# CMD uvicorn app:api --reload
CMD uvicorn app:api

# FROM python:3-slim
# WORKDIR /app
# COPY requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt
# COPY . .
# CMD [ "streamlit", "run",  "app.py"]

# FROM debian:latest
# RUN apt-get update && apt-get install python3-pip -y
# ADD tests_content.py /my_server/tests_content.py
# ADD requirements.txt /my_server/requirements.txt
# WORKDIR /my_server/
# RUN pip3 install -r requirements.txt
# RUN mkdir log
# EXPOSE 8000
# CMD python3 tests_content.py
