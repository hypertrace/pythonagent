# Architecture
![diagram](images/HyperTrace%20Agent%20Architecture.jpg)

# Assumptions
* Tested with [Python v3.7.9](https://www.python.org/downloads/release/python-379/).


# Requirements
* [Python OTel Python Agent](https://github.com/open-telemetry/opentelemetry-python) must not be modified.
* [Python OTel Python Agent](https://github.com/open-telemetry/opentelemetry-python) must be installed (and usable) through pip.
* A set of wrapper classes must be created around each instrumentation module in [Python OTel Python Agent](https://github.com/open-telemetry/opentelemetry-python) to facilitate custom behavior for capturing deeper metrics without modifying those instrumentation modules.
* Initially, 5-10 lines of initialization code can be called from application to be called. Later, we would want to make this transparent.
* Initially extend the [flask framework](https://flask.palletsprojects.com/en/1.1.x/) instrumentation module to capture request and response headers and message bodies. Other instrumentation modules will be done later.
* The span data object for the extended isntrumentation module must match the [Hypertrace specification](https://github.com/hypertrace/specification).
* The Hypertrace Python Agent configuration must match [Agent Configurtion schema](https://github.com/hypertrace/agent-config).
* Use existing test framework in opentelmetry agent to the greatest extent possible.

# Important Links
* [DJango Python Instrumentation Entrypoint](https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-django/src/opentelemetry/instrumentation/django/__init__.py#L59)
* [Flask Python Instrumentation Endpoint](https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-flask/src/opentelemetry/instrumentation/flask/__init__.py#L175)
* [GRPC Python Instrumentation Endpoint](https://github.com/open-telemetry/opentelemetry-python-contrib/blob/7159372e3b381119715c99a37603b3d2d6b9ea46/instrumentation/opentelemetry-instrumentation-grpc/src/opentelemetry/instrumentation/grpc/__init__.py)
* [MySQL Python Instrumentation Entrypoint](https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-mysql/src/opentelemetry/instrumentation/mysql/__init__.py)
* [Hypertrace specification](https://github.com/hypertrace/specification)
* [Agent Configurtion schema](https://github.com/hypertrace/agent-config)
* [Main OTel Python Agent](https://github.com/open-telemetry/opentelemetry-python) - This is the main otel python agent which we would extend
* [Otel Python Contributor](https://github.com/open-telemetry/opentelemetry-python-contrib )
* [Java Agent](https://github.com/hypertrace/javaagent)
* [golang Agent](https://github.com/hypertrace/goagent)
