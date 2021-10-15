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

.. |commits-since| image:: https://img.shields.io/github/commits-since/Emplocity/nameko-chassis/v0.8.0.svg
    :alt: Commits since latest release
    :target: https://github.com/Emplocity/nameko-chassis/compare/v0.8.0...master



.. end-badges

nameko-chassis provides an opinionated base class for building resilient,
observable microservices with the nameko_ framework.

.. _nameko: https://www.nameko.io/


Features
========

By using ``nameko_chassis.service.Service``, you'll get:

 - error reporting using Sentry
 - integrated metrics endpoint for Prometheus
 - request tracing with Zipkin
 - helpers for service discovery (TODO)


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
               self.zipkin.update_binary_annotations({
                  "foo": "bar",
               })
           except Exception:
               self.sentry.captureException()


.. note::
   If the RPC method raises an unhandled exception, nameko-sentry will
   automatically capture it to Sentry. The example above demonstrates the case
   when one wants to access the client manually.

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
