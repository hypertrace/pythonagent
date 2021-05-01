from setuptools import setup, find_packages

exec(open('src/hypertrace/version.py').read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hypertrace",
    version=__version__,
    author="Robert C. Broeckelmann Jr.",
    author_email="robert@iyasec.io",
    description="The Hypertrace Python Agent",
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
    python_requires=">=3.7",
    install_requires=[
        "opentelemetry-api==1.1.0",
        "opentelemetry-exporter-zipkin",
        "opentelemetry-propagator-b3",
        "opentelemetry-exporter-otlp==1.1.0",
        "opentelemetry-instrumentation-flask",
        "opentelemetry-instrumentation-grpc",
        "opentelemetry-instrumentation-mysql",
        "opentelemetry-instrumentation-psycopg2",
        "opentelemetry-instrumentation-requests",
        "opentelemetry-instrumentation-aiohttp_client",
        "opentelemetry-util-http",
        "google",
        "protobuf",
        "pyyaml"
    ]
)
