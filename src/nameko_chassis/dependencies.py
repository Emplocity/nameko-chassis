import logging
import os

from nameko.extensions import DependencyProvider
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler


class SentryLoggerConfig(DependencyProvider):
    def setup(self):
        sentry_config = self.container.config.get("SENTRY", {})
        dsn = sentry_config.get("DSN", None)
        if dsn:
            client = Client(
                dsn, environment=os.environ.get("SENTRY_ENVIRONMENT", "local")
            )
            handler = SentryHandler(client)
            handler.setLevel(logging.ERROR)
            setup_logging(handler)
