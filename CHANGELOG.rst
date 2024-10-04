Changelog
=========

3.0.0 (2024-10-04)
------------------

* Drop support for Python 3.8.
* Add support for Python 3.11 and 3.12.
* Relax upper bounds on transitive dependencies to allow Sentry SDK v2.

2.4.2 (2023-02-06)
------------------

* Use sentry-sdk instead of nameko-sentry with raven

2.3.0 (2023-11-24)
------------------

* Moved build and tool configuration to pyproject.toml

2.2.0 (2023-11-23)
------------------

* Added log informing that service is up and all its dependencies are initialized
* Bump github actions and dev dependencies

2.1.0 (2023-04-05)
------------------

* Move from using flake8 to ruff.

2.0.1 (2022-09-01)
------------------

* Fix obsolete nameko 2 import in is_service_responsive.

2.0.0 (2022-08-25)
------------------

* *BREAKING CHANGE* Drop support for nameko 2. The 2.0 release supports only
  nameko 3.0 RC and higher.
* Add basic configuration for OpenTelemetry tracing.

1.0.0 (2022-07-20)
------------------

* *BREAKING CHANGE* Drop out-of-the-box Zipkin integration.
* Add support for nameko 3.0 RC.
* Add support for Python 3.10.
* Drop support for Python 3.7. The minimum required version is now 3.8.

0.9.0 (2022-04-20)
------------------

* Add ``set_log_level()`` RPC method to dynamically change log level at
  runtime for supported loggers.

0.8.1 (2021-11-12)
------------------

* Add support for Werkzeug 2.0.

0.8.0 (2021-10-15)
------------------

* Add support for Python 3.9.
* Move CI infrastructure to Github Actions.

0.7.0 (2021-03-24)
------------------

* Minimum required Python version is now 3.7.
* Add ``query_state()`` RPC method to access detailed information about
  running service.
* Add ``nameko_chassis.debug`` module intended to debug live services
  with nameko backdoor.

0.6.0 (2020-07-29)
------------------

* Bump minimum version of nameko-prometheus to 1.0. Even though that major
  version changed, this should not be a breaking change.

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
