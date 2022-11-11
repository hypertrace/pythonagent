import sys

from setuptools import setup, find_packages

version_tuple = sys.version_info
# install_requires doesn't always work(like if on older versions of pip)
if sys.version_info < (3, 6):
    print("Hypertrace is not supported on python versions before 3.6")
    sys.exit(1)

exec(open('src/hypertrace/version.py').read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hypertrace-agent",
    version=__version__,
    author="Hypertrace",
    author_email="community@hypertrace.org",
    description="Hypertrace Python Agent",
    long_description="file: README.md",
    long_description_content_type="text/markdown",
    url="https://github.com/hypertrace/pythonagent",
    project_urls={
        "Bug Tracker": "https://github.com/hypertrace/pythonagent/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "opentelemetry-api==1.8.0",
        "opentelemetry-exporter-otlp==1.8.0",
        "opentelemetry-exporter-zipkin==1.8.0",
        "opentelemetry-instrumentation==0.27b0",
        "opentelemetry-instrumentation-aiohttp-client==0.27b0",
        "opentelemetry-instrumentation-boto==0.27b0",
        "opentelemetry-instrumentation-botocore==0.27b0",
        "opentelemetry-instrumentation-wsgi==0.27b0",
        "opentelemetry-instrumentation-fastapi==0.27b0",
        "opentelemetry-instrumentation-flask==0.27b0",
        "opentelemetry-instrumentation-mysql==0.27b0",
        "opentelemetry-instrumentation-psycopg2==0.27b0",
        "opentelemetry-instrumentation-requests==0.27b0",
        "opentelemetry-instrumentation-grpc==0.27b0",
        "opentelemetry-instrumentation-django==0.27b0",
        "opentelemetry-instrumentation-aws-lambda==0.27b0",
        "opentelemetry-propagator-b3==1.8.0",
        "opentelemetry-sdk==1.8.0",
        "opentelemetry-util-http==0.27b0",
        "deprecated==1.2.12",
        "google>=3.0.0",
        "pyyaml",
        "protobuf<=3.19.6"
    ],
    entry_points = {
        'console_scripts': [
            'hypertrace-instrument = hypertrace.agent.autoinstrumentation.hypertrace_instrument:run',
        ],
    }
)
