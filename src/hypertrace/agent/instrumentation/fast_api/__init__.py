"""includes a middleware.__call__ wrapper and the fast api instrumentor implementation + hooks"""
import logging
from functools import wraps

from fastapi import HTTPException
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware, set_status_code
from opentelemetry.instrumentation.asgi import get_host_port_url_tuple, \
    context, extract, asgi_getter, trace, collect_request_attributes

from hypertrace.agent.filter.registry import Registry, TYPE_HTTP
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

logger = logging.getLogger(__name__)  # pylint: disable=C0103


# We need to replace the entire __call__ method so that we can
# pull the req body from the original requests receive
async def replaced_ot_middleware_call(self, scope, receive, send): # pylint:disable=R0914
    """The ASGI application

    Args:
        scope: A ASGI environment.
        receive: An awaitable callable yielding dictionaries
        send: An awaitable callable taking a single dictionary as argument.
    """
    if scope["type"] not in ("http", "websocket"):
        return await self.app(scope, receive, send)

    _, _, url = get_host_port_url_tuple(scope)
    if self.excluded_urls and self.excluded_urls.url_disabled(url):
        return await self.app(scope, receive, send)

    token = context.attach(extract(scope, getter=asgi_getter))
    span_name, additional_attributes = self.default_span_details(scope)

    messages = []
    more_body = True
    while more_body:
        message = await receive()
        messages.append(message)
        more_body = message.get("more_body", False)
    body = b''.join([message.get("body", b"") for message in messages])

    try:
        with self.tracer.start_as_current_span(
                span_name,
                kind=trace.SpanKind.SERVER,
        ) as span:
            if span.is_recording():
                attributes = collect_request_attributes(scope)
                attributes.update(additional_attributes)
                for key, value in attributes.items():
                    span.set_attribute(key, value)

            should_forward_to_handler = True
            if callable(self.server_request_hook):
                should_forward_to_handler = self.server_request_hook(span, scope, body)

            @wraps(receive)
            async def wrapped_receive():
                with self.tracer.start_as_current_span(
                        " ".join((span_name, scope["type"], "receive"))
                ) as receive_span:
                    if messages:
                        return messages.pop(0)
                        # Once that's done we can just await any other messages.
                    if receive_span.is_recording():
                        if message["type"] == "websocket.receive":
                            set_status_code(receive_span, 200)
                        receive_span.set_attribute("type", message["type"])
                    return await receive()

            @wraps(send)
            async def wrapped_send(message):
                send_span = span
                if callable(self.client_response_hook):
                    self.client_response_hook(send_span, message)
                if send_span.is_recording():
                    if message["type"] == "http.response.start":
                        status_code = message["status"]
                        set_status_code(span, status_code)
                    elif message["type"] == "websocket.send":
                        set_status_code(span, 200)
                    elif message["type"] == 'http.response.body':
                        pass
                await send(message)

            if should_forward_to_handler:
                await self.app(scope, wrapped_receive, wrapped_send)
            else:
                set_status_code(span, 403)
                raise HypertraceException(status_code=403)
    finally:
        context.detach(token)


OpenTelemetryMiddleware.__call__ = replaced_ot_middleware_call


class HypertraceException(HTTPException):
    """An exception our middleware will raise if a filter determines to block the request"""

class FastAPIInstrumentorWrapper(BaseInstrumentorWrapper):
    """Used to instrument fast api apps once an app has been loaded """
    def __init__(self):
        super().__init__()
        self.app = None

    def with_app(self, app):
        """Need to defer instrumentation until we have a reference to the fast app
        during fastapi.FastAPI.setup this is invoked and stored so that we can then instrument"""
        self.app = app

    def instrument(self):
        """Adds our error handler as well tracing middleware"""
        if self.app is None:
            print("No app defined, cant instrument fast api")
            return

        async def catch_exceptions_middleware(request: Request, call_next):
            try:
                return await call_next(request)
            except HypertraceException:
                return PlainTextResponse(status_code=403)

        # configure fast api instrumentor w hooks
        FastAPIInstrumentor.instrument_app(app=self.app,
                                           server_request_hook=self.server_request_hook,
                                           client_response_hook=self.client_response_hook)

        # Need to add exception middleware to the top of middleware stack
        # if instrument_app is added after this the exceptions wont be handled by us but by default
        # fast api handler(which results in 500 instead of 403)
        self.app.middleware('http')(catch_exceptions_middleware)

    def server_request_hook(self, span, req_data, body):
        """this function is used to capture request attributes"""
        span.update_name(f"{req_data['method']} {span.name}")
        headers = dict(Headers(raw=req_data['headers']))
        request_url = str(Request(req_data).url)
        self.generic_request_handler(headers, body, span)

        block_result = Registry().apply_filters(span,
                                                request_url,
                                                headers,
                                                body,
                                                TYPE_HTTP)
        if block_result:
            logger.debug('should block evaluated to true, aborting with 403')
            return False
        return True

    def client_response_hook(self, span, resp_data):
        """used to capture the response data
        this function is called twice, once during each resp_phase"""
        resp_phase = resp_data['type']
        if resp_phase == "http.response.start":
            status_code = resp_data["status"]
            set_status_code(span, status_code)
            headers = dict(Headers(raw=resp_data['headers']))
            should_capture_body = self._capture_headers(self._process_response_headers,
                                                        self.HTTP_RESPONSE_HEADER_PREFIX,
                                                        span, headers, self._process_response_body)
            span.set_attribute('hypertrace.capture', should_capture_body)

        elif resp_phase == 'http.response.body':
            should_capture = span.attributes.get('hypertrace.capture')
            if should_capture:
                body_data = resp_data['body']
                body_str = None
                if isinstance(body_data, bytes):
                    body_str = body_data.decode('UTF8', 'backslashreplace')
                else:
                    body_str = body_data

                resp_body_str = self.grab_first_n_bytes(body_str)
                span.set_attribute('http.response.body', resp_body_str)

    def uninstrument(self):
        """Used to uninstrument fast api app"""
        if self.app:
            FastAPIInstrumentor.uninstrument_app(self.app)
