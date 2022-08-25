import logging
import os

from nameko import config
from nameko.containers import WorkerContext
from nameko.extensions import DependencyProvider
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pyrabbit.api import Client
from raven import Client as RavenClient
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from .discovery import ServiceDiscovery


class ContainerProvider(DependencyProvider):
    """
    Allows access to ``ServiceContainer`` running current worker.
    """

    def get_dependency(self, worker_ctx):
        """
        Returns a ``ServiceContainer`` instance which runs current worker.
        """
        return self.container


class SentryLoggerConfig(DependencyProvider):
    def setup(self):
        sentry_config = config.get("SENTRY", {})
        dsn = sentry_config.get("DSN", None)
        if dsn:
            client = RavenClient(
                dsn, environment=os.environ.get("SENTRY_ENVIRONMENT", "local")
            )
            handler = SentryHandler(client)
            handler.setLevel(logging.ERROR)
            setup_logging(handler)


class ServiceDiscoveryProvider(DependencyProvider):
    def __init__(self, management_host: str, username: str, password: str):
        self.management_host = management_host
        self.username = username
        self.password = password

    def get_dependency(self, worker_ctx: WorkerContext) -> ServiceDiscovery:
        client = Client(self.management_host, self.username, self.password)
        return ServiceDiscovery(client)


class OpenTelemetryConfig(DependencyProvider):
    """
    Configures OTel trace exporter over HTTP.
    """

    def setup(self):
        resource = Resource(attributes={SERVICE_NAME: self.container.service_name})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
