import logging
import os

from nameko.containers import ServiceContainer

logger = logging.getLogger(__name__)


class ServiceContainerWithLogging(ServiceContainer):
    def start(self):
        super().start()
        logger.info(
            f"Service {self.service_name} version {os.environ.get('APP_VERSION', 'unknown')} is ready"
        )
