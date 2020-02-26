from unittest.mock import create_autospec

from pyrabbit.api import Client

from nameko_chassis.discovery import ServiceDiscovery


def test_list_services():
    pyrabbit_client = create_autospec(Client)
    pyrabbit_client.host = "localhost:15672"
    pyrabbit_client.get_queues.return_value = [
        {"name": "rpc-my_service", "vhost": "/"},
        {"name": "celery", "vhost": "/"},
        {"name": "rpc-another_service", "vhost": "/"},
    ]
    discovery = ServiceDiscovery(pyrabbit_client)
    services = discovery.find_services()
    assert services == ["my_service", "another_service"]
