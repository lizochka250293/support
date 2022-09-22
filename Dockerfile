FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
