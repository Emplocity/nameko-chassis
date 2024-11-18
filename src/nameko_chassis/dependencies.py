import logging
import os
import sys

import sentry_sdk
from nameko.containers import WorkerContext
from nameko.extensions import DependencyProvider
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pyrabbit.api import Client
from sentry_sdk.integrations.opentelemetry import (  # type: ignore
    SentryPropagator,
    SentrySpanProcessor,
)
from sentry_sdk.utils import BadDsn

from .discovery import ServiceDiscovery

logger = logging.getLogger(__name__)


class ContainerProvider(DependencyProvider):
    """
    Allows access to ``ServiceContainer`` running current worker.
    """

    def get_dependency(self, worker_ctx):
        """
        Returns a ``ServiceContainer`` instance which runs current worker.
        """
        return self.container


class ServiceDiscoveryProvider(DependencyProvider):
    def __init__(self, management_host: str, username: str, password: str):
        self.management_host = management_host
        self.username = username
        self.password = password

    def get_dependency(self, worker_ctx: WorkerContext) -> ServiceDiscovery:
        client = Client(self.management_host, self.username, self.password)
        return ServiceDiscovery(client)


def setup_sentry_sdk(**kwargs) -> None:
    """
    Initialize Sentry integration. Call it once per service container.

    All keywords arguments are forwarded to ``sentry_sdk.init()``
    (with some defaults).
    """
    defaults = {
        "release": os.environ.get("APP_VERSION", None),
        "environment": os.environ.get("SENTRY_ENVIRONMENT", None),
        "dsn": os.environ.get("SENTRY_DSN", None),
        "traces_sample_rate": 1.0,
        "enable_tracing": True,
        "before_send": before_send_filter,
        "before_send_transaction": filter_transactions,
        "instrumenter": "otel",
    }
    params = defaults | kwargs
    if params["dsn"] is None:
        logger.info("Skipped sentry init; no DSN configured")
    else:
        try:
            sentry_sdk.init(**params)
            logger.info("Sentry SDK ready")
        except BadDsn as err:
            logger.exception(
                "Error initializing Sentry integration", extra=dict(error=str(err))
            )
            sys.exit(1)


def before_send_filter(event, hint):
    # also ignore retryable error log messages
    if "log_record" in hint:
        if "Retryable error:" in hint["log_record"].message:
            return None

    return event


def filter_transactions(event, hint):
    if event["transaction"] == "/metrics":
        return None

    return event


def add_sentry_service(service_name: str) -> None:
    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(SentrySpanProcessor())
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    set_global_textmap(SentryPropagator())
