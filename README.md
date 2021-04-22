# Hypertrace OpenTelemetry Python agent
Hypertrace distribution of OpenTelemetry Python agent.

This agent supports these frameworks and adds following capabilities:

* capture request and response headers
* capture request and response bodies
* context propagation/tracing

| Module/Framework | Description | Python Versions Tested/Supported|
|------|-------------| ---------------|
| [flask](https://flask.palletsprojects.com/en/1.1.x/api)|A micro web framework written in Python.| Python 3.7, 3.8, 3.9|
| [grpc](https://grpc.github.io/grpc/python/)|Python GRPC library.| Python 3.7, 3.8, 3.9|
| [mysql-connector](https://dev.mysql.com/doc/connector-python/en/)| Python MySQL database client library.| Python 3.7, 3.8, 3.9|
| [psycopg2/postgresql](https://www.psycopg.org/docs/)|Python Postgresql database client library. | Python 3.8, 3.9|
| [requests](https://docs.python-requests.org/en/master/)|Python HTTP client library.| Python 3.7, 3.8, 3.9|
| [aiohttp](https://docs.aiohttp.org/en/stable/)|Python async HTTP client library.| Python 3.7, 3.8, 3.9|

# Instrument Code
Currently, this agent does not support auto-instrumentation. That will be available in a future release. In the meantime, the following code snippet must be added to the entry point of your python application.

* Have access granted to your github.com id.
* Install the hypertrace python agent:
```
pip install git+https://github.com/traceableai/pythonagent.git@main#egg=hypertrace
```
* Enter your github.com username and password when prompted.
* Add the following to your app's entrypoint python file:
```
from hypertrace.agent import Agent

#
# Code snippet here represents the current initialization logic
# 
# Only add the register functions for instrumentation modules your
# application uses
#
logger.info('Initializing agent.')
agent = Agent()
agent.registerFlaskApp(app) # app is your Flask application object
agent.registerMySQL()
agent.registerPostgreSQL()
agent.registerRequests()
agent.registerAioHttp()
agent.registerGrpcServer()
#
# End initialization logic for Python Agent
#
```

# Environment Variables

| Name | Description |
|------|-------------|
| HT_SERVICE_NAME | Identifies the service/process running e.g. "my service" |
| HT_REPORTING_ENDPOINT | Represents the endpoint for reporting the traces For ZIPKIN reporter type use http://api.traceable.ai:9411/api/v2/spans For OTLP reporter type use http://api.traceable.ai:4317 |
| HT_REPORTING_SECURE | When `true`, connects to endpoints over TLS. |
| HT_REPORTING_TOKEN | User specific token to access Traceable API |
| HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST | When `false` it disables the capture for the request in a client/request operation |
| HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE | When `false` it disables the capture for the response in a client/request operation |
| HT_DATA_CAPTURE_HTTP_BODY_REQUEST | When `false` it disables the capture for the request in a client/request operation |
| HT_DATA_CAPTURE_HTTP_BODY_RESPONSE | When `false` it disables the capture for the response in a client/request operation |
| HT_DATA_CAPTURE_RPC_METADATA_REQUEST | When `false` it disables the capture for the request in a client/request operation |
| HT_DATA_CAPTURE_RPC_METADATA_RESPONSE | When `false` it disables the capture for the response in a client/request operation |
| HT_DATA_CAPTURE_RPC_BODY_REQUEST | When `false` it disables the capture for the request in a client/request operation |
| HT_DATA_CAPTURE_RPC_BODY_RESPONSE | When `false` it disables the capture for the response in a client/request operation |
| HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES | Maximum size of captured body in bytes. Default should be 131_072 (128 KiB). |
| HT_PROPAGATION_FORMATS | List the supported propagation formats e.g. `HT_PROPAGATION_FORMATS="B3,TRACECONTEXT"`. |
| HT_ENABLED | When `false`, disables the agent. |
| HT_LOG_LEVEL | Represents log level. |
| HT_TRACES_EXPORTER | Collector to export traces to e.g `Zipkin`. |
| AGENT_YAML | When `AGENT_YAML` is specified in the environment data would be loaded from that file. |
