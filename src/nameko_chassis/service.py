from nameko.dependency_providers import Config
from nameko.rpc import rpc
from nameko_sentry import SentryReporter
from nameko_zipkin import Zipkin

from .dependencies import SentryLoggerConfig


class Service:
    """
    Base class for nameko services.
    """

    name = "no name"

    SentryLoggerConfig()
    sentry = SentryReporter()
    config = Config()
    zipkin = Zipkin()

    @rpc
    def say_hello(self) -> str:
        """
        RPC method to ping the service to check if it can be reached.
        """
        return f"Hello from {self.name}!"
