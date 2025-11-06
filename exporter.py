from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

# Define service name
resource = Resource(attributes={
    SERVICE_NAME: "viseapijuanes"
})

# ----------- TRACES -----------
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

otlp_span_exporter = OTLPSpanExporter(
    endpoint="https://api.axiom.co/v1/traces",
    headers={
        "Authorization": "Bearer xaat-94e12265-a9e0-4e6b-8945-e0a912dc5833",
        "X-Axiom-Dataset": "viseapi"
    }
)
provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))

service_tracer = trace.get_tracer("viseapi")

# ----------- METRICS -----------
otlp_metric_exporter = OTLPMetricExporter(
    endpoint="https://api.axiom.co/v1/metrics",
    headers={
        "Authorization": "Bearer xaat-94e12265-a9e0-4e6b-8945-e0a912dc5833",
        "X-Axiom-Dataset": "viseapi"
    }
)

metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

service_meter = metrics.get_meter("viseapi")
