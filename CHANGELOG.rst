
Changelog
=========

0.5.0 (2020-03-28)
------------------

* *BREAKING CHANGE* Bump minimum version of nameko-prometheus to 0.2.0. This
  is a breaking change due to how nameko-prometheus is now configured.

0.4.0 (2020-02-27)
------------------

* Add healthcheck/poor man's circuit breaker support.


0.3.1 (2020-02-26)
------------------

* Fix ambiguous Client class names causing incorrect use of raven's Client.

0.3.0 (2020-02-26)
------------------

* Add helpers for service discovery using RabbitMQ management API.

0.2.0 (2020-02-26)
------------------

* Add integrated HTTP ``/metrics`` endpoint to expose Prometheus metrics.

0.1.1 (2020-02-25)
------------------

* Fix bumpversion config causing invalid 'version=0.1.0' version.

0.1.0 (2020-02-25)
------------------

* First usable Service class.

0.0.1 (2020-02-23)
------------------

* First release on PyPI.
