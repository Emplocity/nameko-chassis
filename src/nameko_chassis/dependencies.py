import logging
import sys
import warnings
from typing import Any
from weakref import WeakKeyDictionary

import nameko
import sentry_sdk
from nameko.containers import WorkerContext
from nameko.extensions import DependencyProvider
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pyrabbit.api import Client
from sentry_sdk import Hub
from sentry_sdk.utils import event_from_exception

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


class RavenCompatClient:
    """
    This class provides basic API compatibility layer for legacy projects.

    If you used client dependency from nameko-sentry in your services, this
    class provides a barebones legacy raven API.
    """

    def __init__(self, hub):
        self.hub = hub

    def captureException(self, **kwargs) -> None:
        warnings.warn(
            "captureException() is a legacy API, use sentry_sdk.capture_exception()",
            DeprecationWarning,
            stacklevel=2,
        )
        client = self.hub.client
        exc_info = sys.exc_info()

        event, hint = event_from_exception(
            exc_info,
            client_options=client.options,
            mechanism={"type": "threading", "handled": False},
        )
        res = self.hub.capture_event(event, hint=hint)
        logger.debug(f"capture_event result: {res}")

    def captureMessage(self, message: str, **kwargs) -> None:
        warnings.warn(
            "captureMessage() is a legacy API, use sentry_sdk.capture_message()",
            DeprecationWarning,
            stacklevel=2,
        )
        sentry_sdk.capture_message(message, **kwargs)

    def user_context(self, ctx: dict[str, Any]) -> None:
        warnings.warn(
            "user_context() is a legacy API, use sentry_sdk.set_context()",
            DeprecationWarning,
            stacklevel=2,
        )
        sentry_sdk.set_context("user", ctx)


class ErrorSentryHandler(DependencyProvider):
    """
    Based on https://gist.github.com/puittenbroek/f9de6ddc1fbc1ac838fd46b31c827371
    and https://gist.github.com/zsiciarz/84a358e9bfabc7f4857590e407d77b3b
    """

    def __init__(self):
        self.hubs = WeakKeyDictionary()
        self.main_hub = None

    def setup(self):
        sentry_config = nameko.config.get("SENTRY", {})
        dsn = sentry_config.get("DSN")
        if dsn:
            sentry_sdk.init(dsn)
            self.main_hub = Hub.current
            logger.info("Sentry init completed")
        else:
            logger.warning("Skipped sentry init; no DSN configured")

    def _ensure_hub(self, worker_ctx):
        hub = self.hubs.get(worker_ctx)
        if not hub:
            hub = Hub(self.main_hub)
            self.hubs[worker_ctx] = hub
        return hub

    def worker_setup(self, worker_ctx):
        self._ensure_hub(worker_ctx)

    def get_dependency(self, worker_ctx):
        hub = self._ensure_hub(worker_ctx)
        return RavenCompatClient(hub)

    def worker_result(self, worker_ctx, result=None, exc_info=None):
        if exc_info is None:
            return  # nothing to do

        # Fetch the earlier saved Hub.
        worker_hub = self.hubs.get(worker_ctx)
        if not worker_hub:
            return  # sentry not setup

        # Capture the error in sentry.
        with worker_hub:
            client = worker_hub.client

            event, hint = event_from_exception(
                exc_info,
                client_options=client.options,
                mechanism={"type": "threading", "handled": False},
            )
            res = worker_hub.capture_event(event, hint=hint)
            logger.debug(f"capture_event result: {res}")
