# ── Base: CUDA 12.1 runtime (required by bitsandbytes 4-bit GPU kernels) ─────
# python:3.11-slim has no CUDA — bitsandbytes falls back to CPU without it.
# cuda:12.1.1-runtime is ~1.5 GB but enables 4-bit NF4 on the RTX 3050 (6 GB).
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# ── System Python 3.11 + build essentials ─────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3-pip \
        python3.11-distutils \
        git \
        curl \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ────────────────────────────────────────────────────────
# Copy requirements first so Docker layer-caches the pip install step.
# Re-runs only when requirements.txt changes (not on every source edit).
COPY services/cad-service/requirements.txt .

# Install PyTorch with CUDA 12.1 wheels BEFORE the rest of requirements.
# This ensures torch.cuda.is_available() == True at runtime.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        torch==2.3.1+cu121 \
        torchvision==0.18.1+cu121 \
        --extra-index-url https://download.pytorch.org/whl/cu121 && \
    pip install --no-cache-dir -r requirements.txt

# ── Application source ─────────────────────────────────────────────────────────
COPY packages/ /app/packages/
RUN if [ -d "/app/packages/ai-core" ]; then mv /app/packages/ai-core /app/packages/ai_core; fi
COPY services/cad-service/ /app/services/cad_service/

# ── Environment ────────────────────────────────────────────────────────────────
ENV PYTHONPATH=/app

# HuggingFace model cache — mount a Docker volume here so the
# CAD-Coder weights (~4.5 GB 4-bit) survive container restarts
# and are not re-downloaded on every `docker compose up`.
ENV HF_HOME=/models/hf_cache
ENV HF_HUB_DISABLE_PROGRESS_BARS=0

# Create the cache directory inside the image as a fallback
# (the volume will shadow it when compose mounts it).
RUN mkdir -p /models/hf_cache

# ── Expose & run ───────────────────────────────────────────────────────────────
EXPOSE 8000
CMD ["uvicorn", \
     "services.cad_service.application.cad_service:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--timeout-keep-alive", "300"]
