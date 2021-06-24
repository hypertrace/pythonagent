from setuptools import setup, find_packages

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
        "opentelemetry-api==1.1.0",
        "opentelemetry-exporter-otlp==1.1.0",
        "opentelemetry-exporter-zipkin==1.1.0",
        "opentelemetry-instrumentation==0.20b0",
        "opentelemetry-instrumentation-aiohttp-client==0.20b0",
        "opentelemetry-instrumentation-wsgi==0.20b0",
        "opentelemetry-instrumentation-flask==0.20b0",
        "opentelemetry-instrumentation-mysql==0.20b0",
        "opentelemetry-instrumentation-psycopg2==0.20b0",
        "opentelemetry-instrumentation-requests==0.20b0",
        "opentelemetry-instrumentation-grpc==0.20b0",
        "opentelemetry-propagator-b3==1.1.0",
        "opentelemetry-sdk==1.1.0",
        "opentelemetry-util-http==0.20b0",
        "google>=3.0.0",
        "pyyaml",
        "protobuf>=3.15.8"
    ],
    entry_points = {
        'console_scripts': [
            'hypertrace-instrument = hypertrace.agent.autoinstrumentation.hypertrace_instrument:run',
        ],
    }
)
