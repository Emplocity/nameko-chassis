from nameko.dependency_providers import Config
from nameko.rpc import rpc
from nameko_sentry import SentryReporter
from nameko_zipkin import Zipkin

from .dependencies import SentryLoggerConfig


class Service:
    name = "no name"

    SentryLoggerConfig()
    sentry = SentryReporter()
    config = Config()
    zipkin = Zipkin()

    @rpc
    def say_hello(self) -> str:
        return "Hello from {0}!".format(self.name)
