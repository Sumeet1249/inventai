FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ gfortran libopenblas-dev && rm -rf /var/lib/apt/lists/*
COPY services/physics-service/requirements.txt .
RUN pip install --no-cache-dir protobuf==3.20.3 && \
    pip install --no-cache-dir -r requirements.txt
COPY packages/ /app/packages/
RUN if [ -d "/app/packages/ai-core" ]; then mv /app/packages/ai-core /app/packages/ai_core; fi
COPY services/physics-service/ /app/services/physics_service/
ENV PYTHONPATH=/app
ENV DDE_BACKEND=pytorch
# Fix protobuf descriptor conflict
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
EXPOSE 8000
CMD ["uvicorn", "services.physics_service.application.physics_service:app", "--host", "0.0.0.0", "--port", "8000"]
