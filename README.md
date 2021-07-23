# Hypertrace Python Agent

Python agent provides instrumentation for collecting relevant data to be processed by [Hypertrace](https://www.hypertrace.org/).

This agent supports these frameworks and adds following capabilities:

- capture request and response headers
- capture request and response bodies
- capture SQL queries
- tracing context propagation

| Module/Framework | Description | Python Versions Tested/Supported|
|------|-------------| ---------------|
| [flask](https://flask.palletsprojects.com/en/1.1.x/api)|A micro web framework written in Python.| Python 3.6, 3.7, 3.8, 3.9|
| [grpc](https://grpc.github.io/grpc/python/)|Python GRPC library.| Python 3.6, 3.7, 3.8, 3.9|
| [mysql-connector](https://dev.mysql.com/doc/connector-python/en/)| Python MySQL database client library.| Python 3.6, 3.7, 3.8, 3.9|
| [psycopg2/postgresql](https://www.psycopg.org/docs/)|Python Postgresql database client library. | Python 3.8, 3.9|
| [requests](https://docs.python-requests.org/en/master/)|Python HTTP client library.| Python 3.6, 3.7, 3.8, 3.9|
| [aiohttp](https://docs.aiohttp.org/en/stable/)|Python async HTTP client library.| Python 3.6, 3.7, 3.8, 3.9|

## Getting started

### Instrument Code

Currently, this agent does not support auto-instrumentation. That will be available in a future release. In the meantime, the following code snippet must be added to the entry point of your python application.

- Install the hypertrace python agent:
```bash
pip install hypertrace-agent
```
- Add the following to your app's entrypoint python file:

```python
from hypertrace.agent import Agent

...

agent = Agent() # initialize the agent

# Instrument libraries that are used within your application
agent.register_flask_app(app)  # instrument a flask application
agent.register_mysql()          # instrument the MySQL client
agent.register_postgresql()     # instrument the postgres client
agent.register_grpc_server()    # instrument a grpc server
agent.register_grpc_client()    # instrument a grpc client
agent.register_requests()       # instrument the requests library
agent.register_aiohttp_client() # instrument an aiohttp client
...
```

or

### Use autoinstrumentation 

Hypertrace provides a CLI that will instrument the code without code modification

```
HT_INSTRUMENTED_MODULES=flask,mysql
hypertrace-instrument python app.py
```

By default, all supported modules are instrumented.

For further examples, check our [examples section](./examples)

### Configuration

Pythonagent can be configured using a config file (e.g. env `HT_CONFIG_FILE=./config.yaml`) or passing env vars directly as described in [this list](https://github.com/hypertrace/agent-config/blob/main/ENV_VARS.md)

In some scenarios you may want to configure your agent options programmatically, the following example shows how to achieve this. 
```python
from hypertrace.agent import Agent
from hypertrace.agent.config import config_pb2 as hypertrace_config

agent = Agent()
with agent.edit_config() as config:
    config.service_name = "code modified service name"
    
    config.reporting.endpoint = "http://localhost:4317"
    config.reporting.trace_reporter_type = hypertrace_config.TraceReporterType.OTLP
    config.propagation_formats = [hypertrace_config.PropagationFormat.B3]
```

## Development

### Releases

In order to create a new release, you can run `make release VERSION=<version-number>` and this will change the version in the code appropriately and push the tags.
