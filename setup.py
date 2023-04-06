#!/usr/bin/env python

from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

with open("README.rst", "r") as f:
    long_description = f.read()


setup(
    name="nameko-chassis",
    version="2.1.0",
    license="Apache-2.0",
    description="nameko-chassis provides an opinionated base class for building resilient, observable microservices. ",
    long_description=long_description,
    author="Emplocity",
    author_email="zbigniew.siciarz@emplocity.pl",
    url="https://github.com/Emplocity/nameko-chassis",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://nameko-chassis.readthedocs.io/",
        "Changelog": "https://nameko-chassis.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/Emplocity/nameko-chassis/issues",
    },
    python_requires=">=3.8",
    install_requires=[
        "nameko>=3.0rc11,<4",
        "nameko-sentry>=1.0,<2",
        "nameko-prometheus>=1.5.0,<2",
        "opentelemetry-api>=1.12,<2",
        "opentelemetry-exporter-otlp-proto-http>=1.12,<2",
        "opentelemetry-instrumentation-nameko>=0.3,<1",
        "opentelemetry-sdk>=1.12,<2",
        "opentelemetry-instrumentation-logging>=0.33b0,<1",
        "pyrabbit>=1.1,<2",
        "werkzeug>=1.0,<3",
    ],
)
