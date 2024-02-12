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


def setup_sentry_sdk(service_name: str) -> None:
    app_env = os.environ.get("SENTRY_ENVIRONMENT", "development").lower()
    app_version = os.environ.get("APP_VERSION", None)
    sentry_dsn = os.environ.get("SENTRY_DSN", None)

    if sentry_dsn is None:
        logger.info("Skipped sentry init; no DSN configured")
    else:
        try:
            sentry_sdk.init(
                dsn=sentry_dsn,
                release=app_version,
                environment=app_env,
                traces_sample_rate=1.0,
                enable_tracing=True,
                before_send=before_send_filter,
                before_send_transaction=filter_transactions,
                instrumenter="otel",
            )
            logger.info("Sentry SDK ready")
        except BadDsn as err:
            logger.exception(
                "Error initializing Sentry integration", extra=dict(error=str(err))
            )
            sys.exit(1)

    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(SentrySpanProcessor())
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    set_global_textmap(SentryPropagator())


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
