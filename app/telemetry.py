import os
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from azure.monitor.opentelemetry import configure_azure_monitor

def configure_app(app):
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if connection_string:
        configure_azure_monitor(connection_string=connection_string)

    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()