# NOTE: This file is NOT the active entry point.
# The Dockerfile runs: services.cad_service.application.cad_service:app
# This file is kept only for legacy compatibility. Do not add logic here.
from services.cad_service.application.cad_service import app  # re-export

__all__ = ["app"]
