# Architecture
![diagram](images/HyperTrace%20Agent%20Architecture.jpg)
# Wrapping OpenTelemetry Instrumentation Modules
![diagram](images/OpenTelemetry%20Instrumentation%20Module%20Wrapper.jpg)
# Flask Instrumentation Wrapper Architecture
![diagram](images/FlaskInstrumentationWrapper.jpg)

# Developer Setup
1. clone this repo.
2. run tests: ```scripts/test-all.sh```
3. To run individual tests:
```
cd test/flask
tox
```
# Instrument Code
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
logger.info('Initializing agent.')
agent = Agent()
agent.registerFlaskApp(app)
agent.registerMySQL()
agent.registerPostgreSQL()
agent.registerRequests()
agent.registerAioHttp()
agent.registerGrpcServer()
#
# End initialization logic for Python Agent
#

```

The python agent output is now written to a log file managed by the logging module. This can currently be found in ${REPO_HOME}/test/agent.log.

# Jaeger UI Setup
Hypertrace python agent will use Jaeger backend as OpenTelemetry collector. HyperTrace Python Agent will export OpenTelemetry traces to Jaeger. 
* To run the Jaeger UI docker container, run:
``` $ docker run -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one```
* To Launch Jaeger UI, open a browser and go to:
```http://localhost:16686/search```

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
* [Postgresql Python Instrumentation Entrypoint](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-psycopg2)
* [Hypertrace specification](https://github.com/hypertrace/specification)
* [Hypertrace RPC structure](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/rpc.md)
* [Agent Configurtion schema](https://github.com/hypertrace/agent-config)
* [Main OTel Python Agent](https://github.com/open-telemetry/opentelemetry-python) - This is the main otel python agent which we would extend
* [Otel Python Contributor](https://github.com/open-telemetry/opentelemetry-python-contrib )
* [Java Agent](https://github.com/hypertrace/javaagent)
* [golang Agent](https://github.com/hypertrace/goagent)
* [Python 3 Documentation](https://docs.python.org/3)
* 
# Instrumented Modules Documentation
* [flask](https://flask.palletsprojects.com/en/1.1.x/api) -- Python 3.7, 3.8, 3.9
* [grpc](https://grpc.github.io/grpc/python/) -- Python 3.7, 3.8, 3.9
* [mysql-connector](https://dev.mysql.com/doc/connector-python/en/) -- Python 3.7, 3.8, 3.9
* [psycopg2/postgresql](https://www.psycopg.org/docs/) -- Python 3.8, 3.9
* [requests](https://docs.python-requests.org/en/master/) -- Python 3.7, 3.8, 3.9
* [aiohttp](https://docs.aiohttp.org/en/stable/) -- Python 3.7, 3.8, 3.9

# Base OTel Instrumentation Modules
* [Flask](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-flask)
* [grpc](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-grpc)
* [mysql-connector](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-mysql)
* [psycopg2](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-psycopg2)
* [requests](https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-requests)
* [aiophttp-client](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-aiohttp-client)
* 
# Additional documentation
* [gunicorn](https://docs.gunicorn.org/en/stable/configure.html)

# Build agent-config config.proto
* run: ```protoc --python_out=../agent-config-python -Itools/env-vars-generator/protobuf/src -I. config.proto```
* Python protobuf [example](https://developers.google.com/protocol-buffers/docs/pythontutorial)
* [mysql-connector-python v8.0.5](https://dev.mysql.com/doc/connector-python/en/)
* [postgresql modules - don't have specifics yet](https://wiki.postgresql.org/wiki/Python)

# Sample Agent config file
```
reporting:
  endpoint: "http://localhost:9411/api/v2/spans"
  secure: false
data_capture:
  http_headers:
    request: true
    response: true
  http_body:
    request: true
    response: true
  rpc_metadata:
    request: true
    response: true
  rpc_body:
    request: true
    response: true
```
# Sample Hypertrace Extended Span for Flask Framework
```
{
    "name": "/",
    "context": {
        "trace_id": "0x33b5ed7d2425b50544e30b00ab2940f1",
        "span_id": "0x178b481b3e8d0be1",
        "trace_state": "[]"
    },
    "kind": "SpanKind.SERVER",
    "parent_id": null,
    "start_time": "2021-03-12T01:30:25.440868Z",
    "end_time": "2021-03-12T01:30:25.454422Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "http.method": "GET",
        "http.server_name": "127.0.0.1",
        "http.scheme": "http",
        "net.host.port": 5000,
        "http.host": "localhost:5000",
        "http.target": "/",
        "net.peer.ip": "127.0.0.1",
        "http.user_agent": "curl/7.66.0",
        "net.peer.port": 50096,
        "http.flavor": "1.1",
        "http.route": "/",
        "http.request.header.Host": "localhost:5000",
        "http.request.header.User-Agent": "curl/7.66.0",
        "http.request.header.Accept": "*/*",
        "http.request.header.Tester1": "tester1",
        "http.request.header.Tester2": "tester2",
        "http.request.body": "b''",
        "http.response.header.Content-Type": "text/html; charset=utf-8",
        "http.response.header.tester3": "tester3",
        "http.response.header.Content-Length": "24",
        "http.response.body": "b\"{'a': 'a', 'xyz': 'xyz'}\"",
        "http.status_text": "OK",
        "http.status_code": 200
    },
    "events": [],
    "links": [],
    "resource": {
        "telemetry.sdk.language": "python",
        "telemetry.sdk.name": "opentelemetry",
        "telemetry.sdk.version": "1.0.0rc1",
        "service.name": "unknown_service"
    }
}
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
# Testing tools
* [tox](https://tox.readthedocs.io/en/latest/)
* [pytest](https://docs.pytest.org/en/stable/contents.html)
* [gunicorn + flask + nginx Example]( https://github.com/ivanpanshin/flask_gunicorn_nginx_docker) -- used as the basis for the gunicorn tests.

# Documentation
Documentation is generated by [pdoc3](https://pypi.org/project/pdoc3/)
