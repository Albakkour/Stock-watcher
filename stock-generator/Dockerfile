FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379


ENV RABBIT_HOST=rabbitmq
ENV RABBIT_USER=appuser
ENV RABBIT_PASS=apppass

ENV STOCK_SYMBOLS=TSLA,AAPL,MSFT,NVDA,GOOG
ENV UPDATE_PERIOD=15.0

CMD ["python", "worker.py"]
