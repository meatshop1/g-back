FROM python:3.11.9-slim

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=meatshop.settings.dev
WORKDIR /app

# Install system dependencies for MySQL
RUN apt-get update \
  && apt-get install -y python3-dev default-libmysqlclient-dev gcc \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Ensure pip is installed and upgraded
RUN python -m ensurepip --default-pip && pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

