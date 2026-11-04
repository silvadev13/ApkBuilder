FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV PYTHONPATH="/app:/app/BorderP45"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "BorderP45.app:app"]
