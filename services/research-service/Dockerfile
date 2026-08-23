FROM python:3.11-slim
WORKDIR /app
COPY services/research-service/requirements.txt .
RUN pip install --no-cache-dir protobuf==3.20.3 && \
    pip install --no-cache-dir -r requirements.txt
COPY packages/ /app/packages/
RUN if [ -d "/app/packages/ai-core" ]; then mv /app/packages/ai-core /app/packages/ai_core; fi
COPY services/research-service/ /app/services/research_service/
ENV PYTHONPATH=/app
# Fix protobuf descriptor conflict with chromadb + opentelemetry
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
EXPOSE 8000
CMD ["uvicorn", "services.research_service.application.research_service:app", "--host", "0.0.0.0", "--port", "8000"]
