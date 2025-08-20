FROM mcr.microsoft.com/playwright/python:v1.51.0-noble
LABEL authors="kivar"

WORKDIR /bot

COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip
RUN pip install --upgrade setuptools wheel
RUN pip cache purge

RUN apt-get update && apt-get install -y ffmpeg liblz4-dev python3-dev build-essential

RUN pip install --no-cache-dir --prefer-binary lz4 --break-system-packages

RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

RUN playwright install

COPY . .

ENV PORT=8080

EXPOSE 8080

CMD [ "python", "-u", "./bot.py" ]