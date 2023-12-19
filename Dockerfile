FROM python:3.10

# create the queue folder
WORKDIR /var/whisper

# create the app folder.
WORKDIR /usr/src/app

COPY auto-scanner.py ./
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -U openai-whisper

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install ffmpeg -y
RUN pip install setuptools-rust

# run with unbuffered output.
CMD [ "python", "-u", "./auto-scanner.py", "/var/whisper" ]