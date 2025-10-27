import os
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from azure.monitor.opentelemetry import configure_azure_monitor
app = FastAPI()

# Configure Azure Monitor
configure_azure_monitor(
 connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
)

FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()
@app.get("/")
async def root():
 return {"message": "Hello from FastAPI with App Insights!"}