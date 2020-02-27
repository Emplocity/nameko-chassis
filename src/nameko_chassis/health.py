import logging

import eventlet
from nameko.rpc import ServiceProxy

logger = logging.getLogger(__name__)


class ServiceTimeout(Exception):
    pass


def is_service_responsive(
    service_proxy: ServiceProxy,
    fail_gracefully=False,
    timeout: float = 5,
    method_name: str = "say_hello",
) -> bool:
    """
    A poor man's circuit breaker for nameko service proxies.

    True circuit breaker would wrap each and every RPC method and monitor
    it's error rate and duration. This implementation only checks if the
    service responds within ``timeout`` seconds. By default, it raises
    an exception if service is unreachable. However if ``fail_gracefully``
    is ``True``, function returns normally and it is up to the caller
    to implement some sort of fallback mechanism.

    :param service_proxy: nameko service proxy provided by ``RPCProxy``
    :param fail_gracefully: if ``True``, don't raise ``ServiceTimeout``
    :param timeout: timeout in seconds
    :param method_name: which method to call to check if service is healthy
    :raises: ServiceTimeout: if service is unresponsive and
        ``fail_gracefully`` is False
    :return: ``True`` if service is responsive
    """
    try:
        with eventlet.Timeout(timeout, ServiceTimeout):
            method = getattr(service_proxy, method_name)
            method()
            return True
    except ServiceTimeout:
        message = f"{service_proxy.service_name} is unreachable after {timeout} seconds"
        logger.warning(message)
        if fail_gracefully:
            return False
        else:
            raise ServiceTimeout(message)
