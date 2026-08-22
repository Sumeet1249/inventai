FROM python:3.11-slim

WORKDIR /app

COPY services/business-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared packages if needed
COPY packages/ /app/packages/
RUN if [ -d "/app/packages/ai-core" ]; then mv /app/packages/ai-core /app/packages/ai_core; fi

COPY services/business-service/ /app/services/business_service/

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "services.business_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
