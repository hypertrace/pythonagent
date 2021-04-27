# Hypertrace Python Agent

Python agent provides instrumentation for collecting relevant data to be processed by [Hypertrace](https://www.hypertrace.org/).

This agent supports these frameworks and adds following capabilities:

- capture request and response headers
- capture request and response bodies
- capture SQL queries
- tracing context propagation

| Module/Framework | Description | Python Versions Tested/Supported|
|------|-------------| ---------------|
| [flask](https://flask.palletsprojects.com/en/1.1.x/api)|A micro web framework written in Python.| Python 3.7, 3.8, 3.9|
| [grpc](https://grpc.github.io/grpc/python/)|Python GRPC library.| Python 3.7, 3.8, 3.9|
| [mysql-connector](https://dev.mysql.com/doc/connector-python/en/)| Python MySQL database client library.| Python 3.7, 3.8, 3.9|
| [psycopg2/postgresql](https://www.psycopg.org/docs/)|Python Postgresql database client library. | Python 3.8, 3.9|
| [requests](https://docs.python-requests.org/en/master/)|Python HTTP client library.| Python 3.7, 3.8, 3.9|
| [aiohttp](https://docs.aiohttp.org/en/stable/)|Python async HTTP client library.| Python 3.7, 3.8, 3.9|

## Getting started

### Instrument Code

Currently, this agent does not support auto-instrumentation. That will be available in a future release. In the meantime, the following code snippet must be added to the entry point of your python application.

- Install the hypertrace python agent:
```bash
pip install git+https://github.com/hypertrace/pythonagent.git@main#egg=hypertrace
```
- Add the following to your app's entrypoint python file:

```python
from hypertrace.agent import Agent

...

agent = Agent() # initialize the agent
agent.registerFlaskApp(app) # instrument a flask application
agent.registerMySQL() # instrument the MySQL client
...
```

For further examples, check our [examples section](./examples)

### Configuration

Pythonagent can be configured using a config file (e.g. env `HT_CONFIG_FILE=./config.yaml`) or passing env vars directly as described in [this list](https://github.com/hypertrace/agent-config/blob/main/ENV_VARS.md)
