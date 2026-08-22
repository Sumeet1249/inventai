FROM python:3.11-slim
WORKDIR /app
COPY services/patent-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY packages/ /app/packages/
RUN if [ -d "/app/packages/ai-core" ]; then mv /app/packages/ai-core /app/packages/ai_core; fi
COPY services/patent-service/ /app/services/patent_service/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "services.patent_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
