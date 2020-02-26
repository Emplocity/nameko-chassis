import logging
from typing import List

from pyrabbit.api import Client

logger = logging.getLogger(__name__)


class ServiceDiscovery:
    """
    Provides introspection for nameko services defined on the RabbitMQ cluster.
    """

    def __init__(self, client: Client):
        self.client = client
        logger.info(f"Service discovery ready: host={self.client.host}")

    def find_services(self) -> List[str]:
        """
        Returns a list of service names which are available on the network.
        """
        return [
            queue["name"].replace("rpc-", "")
            for queue in self.client.get_queues()
            if self.is_nameko_service(queue["name"])
        ]

    def is_nameko_service(self, queue_name: str) -> bool:
        """
        Checks if queue name matches pattern used by nameko for service queues.
        """
        return queue_name.startswith("rpc-") and queue_name.endswith("_service")
