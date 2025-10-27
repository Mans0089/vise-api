from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


def setup_tracer(service_name: str):
    """Configura un tracer conectado directamente a Grafana Cloud."""

    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(
        endpoint="https://otlp-gateway-prod-us-east-2.grafana.net/otlp/v1/traces",
        headers={
            "Authorization": "Basic MTQxMTUwMjpnbGNfZXlKdklqb2lNVFUyTlRrd05pSXNJbTRpT2lKd2VYUm9iMjR0ZEc5clpXNGlMQ0pySWpvaU1HTnJaVEE1VTNSeVR6RklNakZLVkVVNFFUVTRaRE5xSWl3aWJTSTZleUp5SWpvaWNISnZaQzExY3kxbFlYTjBMVEFpZlgwPQ=="
        },
        timeout=10,
    )

    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)