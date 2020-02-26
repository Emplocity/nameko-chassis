import logging
import os

from nameko.containers import WorkerContext
from nameko.extensions import DependencyProvider
from pyrabbit.api import Client
from raven import Client as RavenClient
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from .discovery import ServiceDiscovery


class SentryLoggerConfig(DependencyProvider):
    def setup(self):
        sentry_config = self.container.config.get("SENTRY", {})
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

    def setup(self):
        self.client = Client(self.management_host, self.username, self.password)
        self.discovery = ServiceDiscovery(self.client)

    def get_dependency(self, worker_ctx: WorkerContext) -> ServiceDiscovery:
        return self.discovery
