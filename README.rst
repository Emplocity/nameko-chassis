========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |coveralls|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/nameko-chassis/badge/?style=flat
    :target: https://readthedocs.org/projects/nameko-chassis
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/Emplocity/nameko-chassis.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Emplocity/nameko-chassis

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

.. |commits-since| image:: https://img.shields.io/github/commits-since/Emplocity/nameko-chassis/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/Emplocity/nameko-chassis/compare/v0.0.1...master



.. end-badges

nameko-chassis provides an opinionated base class for building resilient,
observable microservices with the nameko_ framework.

.. _nameko: https://www.nameko.io/


Features
========

By using ``nameko_chassis.Service``, you'll get:

 - error reporting using Sentry
 - integrated metrics endpoint for Prometheus
 - request tracing with Zipkin
 - helpers for service discovery


Installation
============

::

    pip install nameko-chassis

You can also install the in-development version with::

    pip install https://github.com/Emplocity/nameko-chassis/archive/master.zip


Usage
=====

TODO: basic example


Documentation
=============


https://nameko-chassis.readthedocs.io/


Development
===========

To run the all tests run::

    tox


Authors
=======

``nameko-prometheus`` is developed and maintained by `Emplocity`_.

.. _Emplocity: https://emplocity.com/


License
=======

This work is released under the Apache 2.0 license.
