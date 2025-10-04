"""
WSGI config for webapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Initialize OpenTelemetry before Django
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Set up OpenTelemetry
jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("TRACING_HOST", "jaeger"),
    agent_port=int(os.getenv("TRACING_PORT", "6831")),
)

trace.set_tracer_provider(TracerProvider(
    resource=Resource.create({
        SERVICE_NAME: 'webapp-service'
    })
))

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Django and other libraries
DjangoInstrumentor().instrument()
LoggingInstrumentor().instrument()
RequestsInstrumentor().instrument()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')

application = get_wsgi_application()