FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt /app
COPY templates /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 2000

CMD ["python", "app.py"]