FROM python:3.11-slim
WORKDIR /app
COPY services/innovation-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY packages/ /app/packages/
RUN if [ -d "/app/packages/ai-core" ]; then mv /app/packages/ai-core /app/packages/ai_core; fi
COPY services/innovation-engine/ /app/services/innovation_engine/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "services.innovation_engine.application.innovation_service:app", "--host", "0.0.0.0", "--port", "8000"]
