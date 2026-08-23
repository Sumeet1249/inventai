FROM python:3.11-slim
WORKDIR /app
COPY services/circuit-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/circuit-service/ /app/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
