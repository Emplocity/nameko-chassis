.. include-section-overview-start

==============
nameko-chassis
==============

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |actions|
        | |coveralls|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/nameko-chassis/badge/?style=flat
    :target: https://readthedocs.org/projects/nameko-chassis
    :alt: Documentation Status

.. |actions| image:: https://github.com/Emplocity/nameko-chassis/actions/workflows/build.yml/badge.svg
    :alt: Github Actions Build Status
    :target: https://github.com/Emplocity/nameko-chassis/actions/

.. |coveralls| image:: https://coveralls.io/repos/Emplocity/nameko-chassis/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/Emplocity/nameko-chassis

.. |version| image:: https://img.shields.io/pypi/v/nameko-chassis.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/nameko-chassis

.. |wheel| image:: https://img.shields.io/pypi/wheel/nameko-chassis.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/nameko-chassis

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/nameko-chassis.svg
    :alt: Supported versions
    :target: https://pypi.org/project/nameko-chassis

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/nameko-chassis.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/nameko-chassis

.. |commits-since| image:: https://img.shields.io/github/commits-since/Emplocity/nameko-chassis/v3.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/Emplocity/nameko-chassis/compare/v3.1.0...master



.. end-badges

nameko-chassis provides an opinionated base class for building resilient,
observable microservices with the nameko_ framework.

.. _nameko: https://www.nameko.io/


nameko-chassis releases and distributed tracing
===============================================

We've changed the approach to distributed tracing over a few releases. Here's
an overview:

- 0.9.0 supports only nameko 2 and has Zipkin integration
- 1.0 supports both nameko 2 and 3 RC, while dropping Zipkin. If
  you need Zipkin support and your service is still on nameko 2, either stay on
  nameko-chassis 0.9, or upgrade to 1.x and manage nameko-zipkin yourself.
- 2.0 supports only nameko v3 and provides a predefined OpenTelemetry
  integration to base Service class. You can still use OpenTelemetry with
  nameko-chassis 1.0 (provided you're using nameko 3), but before 2.0 you'll
  need to set it up yourself.


Features
========

By using ``nameko_chassis.service.Service``, you'll get:

- error reporting using Sentry
- integrated metrics endpoint for Prometheus
- helpers for service discovery
- partial\* support for OpenTelemetry tracing

\*You'll need to call the instrumentors yourself, but we provide basic
configuration as a dependency provider.


Installation
============

::

    pip install nameko-chassis

You can also install the in-development version with::

    pip install https://github.com/Emplocity/nameko-chassis/archive/master.zip

.. include-section-overview-end


Usage
=====

.. include-section-usage-start

Base service class
------------------

.. code-block:: python

   from nameko.rpc import rpc
   from nameko_chassis.service import Service


   class MyService(Service):
       name = "my_service"

       @rpc
       def my_method(self):
           try:
               do_something()
           except Exception:
               self.sentry.captureException()


.. note::
   If the RPC method raises an unhandled exception, nameko-sentry will
   automatically capture it to Sentry. The example above demonstrates the case
   when one wants to access the client manually.

Distributed tracing
-------------------

Since nameko-chassis 2.0, we provide an opinionated setup of OpenTelemetry.
Your services will export traces over HTTP to an endpoint defined in
``OTEL_EXPORTER_OTLP_ENDPOINT`` environment variable. However, you need to
call instrumentors yourself, for example:

.. code-block:: python

   from nameko_chassis.service import Service
   from nameko_opentelemetry import NamekoInstrumentor
   from opentelemetry.instrumentation.logging import LoggingInstrumentor

   LoggingInstrumentor().instrument()

   NamekoInstrumentor().instrument(
       send_headers=True,
       send_request_payloads=True,
       send_response_payloads=True,
       max_truncate_length=1000,
   )

   class MyService(Service):
       name = "my_service"


.. note::
   We chose HTTP over GRPC due to incompatibilities between eventlet and grpc
   with regards to asynchronous runtime.

Backdoor debugging
------------------

``nameko-chassis.debug`` includes helpers for introspecting running services
with nameko backdoor feature. For example if your service exposes backdoor
on port 12345::

    $ rlwrap nc -v localhost 12345
    Connection to localhost 12345 port [tcp/*] succeeded!
    Python 3.8.8 (default, Mar 23 2021, 11:02:14)
    [GCC 9.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> from nameko_chassis.debug import debug_runner
    >>> debug_runner(runner)
    ╭──────────────────────────── sleeping_http_service ───────────────────────────╮
    │ 19 entrypoints                                                               │
    │ 15 dependencies                                                              │
    │ running 1/10 worker threads                                                  │
    │ ╭────────────────── Thread #0: SleepingHttpService.sleep ──────────────────╮ │
    │ │                                                                          │ │
    │ │ Args: ["<Request 'http://127.0.0.1:8000/sleep/500' [GET]>"]              │ │
    │ │ Kwargs: {'duration': '500'}                                              │ │
    │ │ Context data: {'X-B3-ParentSpanId': '1058ef878ab0fe32'}                  │ │
    │ │                                                                          │ │
    │ │ Traceback:                                                               │ │
    │ │   File                                                                   │ │
    │ │ "/home/zbigniewsiciarz/v/sleephttp/lib/python3.8/site-packages/eventlet… │ │
    │ │ line 221, in main                                                        │ │
    │ │     result = function(*args, **kwargs)                                   │ │
    │ │   File                                                                   │ │
    │ │ "/home/zbigniewsiciarz/v/sleephttp/lib/python3.8/site-packages/nameko/c… │ │
    │ │ line 392, in _run_worker                                                 │ │
    │ │     result = method(*worker_ctx.args, **worker_ctx.kwargs)               │ │
    │ │   File "./app/service.py", line 73, in sleep                             │ │
    │ │     time.sleep(duration)                                                 │ │
    │ │   File                                                                   │ │
    │ │ "/home/zbigniewsiciarz/v/sleephttp/lib/python3.8/site-packages/eventlet… │ │
    │ │ line 36, in sleep                                                        │ │
    │ │     hub.switch()                                                         │ │
    │ │   File                                                                   │ │
    │ │ "/home/zbigniewsiciarz/v/sleephttp/lib/python3.8/site-packages/eventlet… │ │
    │ │ line 313, in switch                                                      │ │
    │ │     return self.greenlet.switch()                                        │ │
    │ │                                                                          │ │
    │ ╰──────────────────────────────────────────────────────────────────────────╯ │
    ╰──────────────────────────────────────────────────────────────────────────────╯

.. note:: Pretty printing like in the above example requires rich_.

    .. _rich: https://github.com/willmcgugan/rich

.. include-section-usage-end

Documentation
=============

https://nameko-chassis.readthedocs.io/


Development
===========

To run the all tests run::

    tox


Authors
=======

``nameko-chassis`` is developed and maintained by `Emplocity`_.

.. _Emplocity: https://emplocity.com/


License
=======

This work is released under the Apache 2.0 license.
