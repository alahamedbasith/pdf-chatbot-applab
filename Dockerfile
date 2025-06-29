FROM python:3.12.6-slim

WORKDIR /

COPY requirements.txt /app/requirements.txt
COPY app /app
COPY static /static
COPY templates /templates

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0"]
