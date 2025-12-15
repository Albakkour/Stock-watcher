# FROM python:3.11-slim
FROM gitlab.control.lth.se:5050/regler/frtn90/2025/agroup01/python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
