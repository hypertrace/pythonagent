# Hypertrace Python Agent

Python agent provides instrumentation for collecting relevant data to be processed by [Hypertrace](https://www.hypertrace.org/).

This agent supports these frameworks and adds following capabilities:

- capture request and response headers
- capture request and response bodies
- capture SQL queries
- tracing context propagation


Hypertrace python agent supports Python 3.6+

| Library | Description | Supported Library Versions|
|------|-------------| ---------------|
| [flask](https://flask.palletsprojects.com/en/1.1.x/api)|A micro web framework written in Python.| 1.\*, 2.\*|
| [django](https://docs.djangoproject.com/)|Python web framework | 1.10+|
| [grpc](https://grpc.github.io/grpc/python/)|Python GRPC library.| 1.27+|
| [mysql-connector](https://dev.mysql.com/doc/connector-python/en/)| Python MySQL database client library.| 8.\*|
| [psycopg2/postgresql](https://www.psycopg.org/docs/)|Python Postgresql database client library. | 2.7.3.1+ |
| [requests](https://docs.python-requests.org/en/master/)|Python HTTP client library.| 2.\*|
| [aiohttp](https://docs.aiohttp.org/en/stable/)|Python async HTTP client library.| 3.\*|

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


### Lambda Integration
In order to use the agent in an aws lambda, first publish a layer to your AWS account. 

You must have the [aws cli](https://aws.amazon.com/cli/) & [sam](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed. 

From the root of this repo run: 
`./build_layer.sh <region to deploy layer to> <python version target>`
ex: `./build_layer.sh us-east-2 python38`

The region should match the region of the lambda you are instrumenting.
The python version should match the version of the python runtime you are instrumenting.

If you have multiple versions of python runtimes, you can publish a layer for each python version(3.6, 3.7, 3.8, 3.9)
by running: `./build_all_layers.sh us-east-2`

The script will print out the ARN for the lambda layer:
```bash
python3.9 Layer ARN:
arn:aws:lambda:us-east-2:286278240186:layer:hypertrace-layer-python39:6
```

Once the layer is deployed you can add the layer to the lambda either via a SAM template, or via the Lambda UI. 

If you are deploying your lambda via a SAM template, you will need to add the `Layers` key:
ex: 

```yaml
ServerlessFunction:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: .
    Handler: your_handler
    Runtime: Python3.7
    Layers:
        - Enter the copy pasted ARN here
    Environment:
        Variables:
          AWS_LAMBDA_EXEC_WRAPPER: /opt/hypertrace-instrument
```

## Development
To run tests locally:

1.) `pip install -r requirements -r dev-requirements.txt`

2.) `python setup.py develop`

3.) `python -m pytest tests/hypertrace`

### Generating Protobuf

If you need to upgrade the agent-config submodule, & therefor need to re-generate the python protobuf files, you should use the provided `proto.sh` script.

Example: 

`./proto.sh <OS>`(osx, linux, win32 or win64) - this ensures that the python protobuf files are built on a consistent version of protoc

### Releases

In order to create a new release, you can run `make release VERSION=<version-number>` and this will change the version in the code appropriately and push the tags.
