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
| [django](https://docs.djangoproject.com/)|Python web framework | Python 3.6, 3.7, 3.8, 3.9|
| [grpc](https://grpc.github.io/grpc/python/)|Python GRPC library.| Python 3.6, 3.7, 3.8, 3.9|
| [mysql-connector](https://dev.mysql.com/doc/connector-python/en/)| Python MySQL database client library.| Python 3.6, 3.7, 3.8, 3.9|
| [psycopg2/postgresql](https://www.psycopg.org/docs/)|Python Postgresql database client library. | Python 3.8, 3.9|
| [requests](https://docs.python-requests.org/en/master/)|Python HTTP client library.| Python 3.6, 3.7, 3.8, 3.9|
| [aiohttp](https://docs.aiohttp.org/en/stable/)|Python async HTTP client library.| Python 3.6, 3.7, 3.8, 3.9|

## Getting started

## Instrumentation
The hypertrace agent offers two methods of instrumenting your python application.
- Manual instrumentation requires editing your code to initialize an agent, and registering any applicable modules to be instrumented.
- Auto instrumentation involves prepending your applications startup command with `hypertrace-instrument`.

Both approaches are explained in more detail below.

### Manual Instrumentation

- Install the hypertrace python agent:
```bash
pip install hypertrace-agent
```
- Add the following to your app's entrypoint python file:

```python
from hypertrace.agent import Agent

agent = Agent() # initialize the agent

# Instrument a specific flask app + any other applicable libraries
agent.instrument(app)

# Instrument a flask app, additional libraries, except for mysql
# the second arg tells the agent to skip these specific libraries from being instrumented
agent.instrument(app, ['mysql'])


# if you aren't using flask, you can pass None
# and still provide skip libraries if needed
agent.instrument(None, ['flask', 'mysql'])
...
```

_Note: The `HT_SKIP_MODULES` environment variable does not have any effect for manual instrumentation_

### Autoinstrumentation
Hypertrace provides a CLI that will instrument the code without code modification

```
HT_SKIP_MODULES=flask,mysql
hypertrace-instrument python app.py
```

By default, all supported modules are instrumented.

When using auto instrumentation you can use the `HT_SKIP_MODULES` environment variable to limit which modules are instrumented.
In the above example, flask and mysql would not be instrumented

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

### Autoinstrumentation with pre-fork web servers
If you are using Python > 3.7 forked worker processes will also be instrumented automatically

If you are using Python 3.6 please see below for a gunicorn example.

Add the following code snippet to your gunicorn config file, or create one if you don't already use a config file.
```python
# gunicorn_config.py
import hypertrace

def post_fork(server, worker):
    hypertrace.post_fork(server, worker)
```

You would then reference the config file in your `gunicorn` launch command:
ex: 
<pre>
hypertrace-instrument gunicorn -w 5 -b 0.0.0.0:5000 wsgi:app <b>-c gunicorn_config.py</b>
</pre>


## Development

### Releases

In order to create a new release, you can run `make release VERSION=<version-number>` and this will change the version in the code appropriately and push the tags.
