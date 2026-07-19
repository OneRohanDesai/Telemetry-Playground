import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_telemetry(service_name: str):

    resource = Resource.create(
        {
            "service.name": service_name,
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint="otel-collector.observability.svc.cluster.local:4317",
        insecure=True,
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    return trace.get_tracer(os.getenv("OTEL_SERVICE_NAME", service_name))


exporter = OTLPSpanExporter(
    endpoint=os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://otel-collector.observability.svc.cluster.local:4317",
    ),
    insecure=True,
)
