FROM python:3.11-slim
WORKDIR /app
COPY services/ai-agent-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY packages/ /app/packages/
RUN if [ -d "/app/packages/ai-core" ]; then mv /app/packages/ai-core /app/packages/ai_core; fi
# Rename hyphenated folder to valid Python package name
COPY services/ai-agent-service/ /app/services/ai_agent_service/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "services.ai_agent_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
