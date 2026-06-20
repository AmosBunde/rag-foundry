import logging
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.config import settings

# Prometheus metrics
registry = CollectorRegistry()
REQUEST_COUNT = Counter(
    "corrective_rag_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)
REQUEST_LATENCY = Histogram(
    "corrective_rag_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    registry=registry,
)
CORRECTIVE_ITERATIONS = Histogram(
    "corrective_rag_iterations",
    "Number of corrective retrieval iterations performed",
    buckets=[1, 2, 3, 4],
    registry=registry,
)
CONFIDENCE_SCORE = Histogram(
    "corrective_rag_confidence_score",
    "Final confidence score distribution",
    buckets=[0.0, 0.25, 0.5, 0.75, 0.9, 1.0],
    registry=registry,
)
FEEDBACK_COUNT = Counter(
    "corrective_rag_feedback_total",
    "User feedback submissions",
    ["helpful"],
    registry=registry,
)


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))


def configure_tracing(app: FastAPI) -> None:
    resource = Resource(attributes={SERVICE_NAME: settings.app_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    if settings.environment == "development":
        exporter = ConsoleSpanExporter()
    else:
        exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    FastAPIInstrumentor.instrument_app(app)


async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    path = request.url.path
    method = request.method
    status = str(response.status_code)

    REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    configure_tracing(app)
    yield


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(registry), CONTENT_TYPE_LATEST
