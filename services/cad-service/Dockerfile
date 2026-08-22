FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 && rm -rf /var/lib/apt/lists/*
COPY services/cad-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY packages/ /app/packages/
RUN if [ -d "/app/packages/ai-core" ]; then mv /app/packages/ai-core /app/packages/ai_core; fi
COPY services/cad-service/ /app/services/cad_service/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "services.cad_service.application.cad_service:app", "--host", "0.0.0.0", "--port", "8000"]
