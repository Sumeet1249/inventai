import os
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_telemetry(app: FastAPI, service_name: str):
    """
    Initializes OpenTelemetry tracing and exports to Jaeger via OTLP.
    """
    # Set the service name for traces
    os.environ.setdefault("OTEL_SERVICE_NAME", service_name)
    
    provider = TracerProvider()
    
    # Send traces to Jaeger container over grpc
    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://inventai-jaeger:4317")
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    
    # Auto-instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    return provider
