'''Hypertrace wrapper around OTel Lambda Instrumentor'''  # pylint: disable=R0801
import logging
import os
from typing import Any, Callable
from wrapt import wrap_function_wrapper

from opentelemetry.instrumentation.aws_lambda import AwsLambdaInstrumentor
from opentelemetry.context.context import Context
from opentelemetry.instrumentation.aws_lambda.version import __version__
from opentelemetry.instrumentation.aws_lambda import _default_event_context_extractor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import (
    SpanKind,
    TracerProvider,
    get_tracer,
    get_tracer_provider,
)
from opentelemetry.instrumentation import aws_lambda

from hypertrace.agent.instrumentation import BaseInstrumentorWrapper
logger = logging.getLogger(__name__)  # pylint: disable=C0103


class AwsLambdaInstrumentorWrapper(AwsLambdaInstrumentor, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel Lambda Instrumentor'''

    def __init__(self):
        '''Constructor'''
        logger.debug('Entering AwsLambdaInstrumentorWrapper.__init__().')
        super().__init__()

    # We need to replace default _instrument behavior to capture request/resp data
    def _ht_instrument(self,
            wrapped_module_name,
            wrapped_function_name,
            event_context_extractor: Callable[[Any], Context],
            tracer_provider: TracerProvider = None,
    ):
        wrapper_instance = self
        def _instrumented_lambda_handler_call( # pylint:disable=R0914
                call_wrapped, _instance, args, kwargs
        ):

            orig_handler_name = ".".join(
                [wrapped_module_name, wrapped_function_name]
            )

            lambda_event = args[0]


            parent_context = aws_lambda._determine_parent_context(  # pylint:disable=W0212
                lambda_event, event_context_extractor
            )

            # See more:
            # https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
            try:
                if lambda_event["Records"][0]["eventSource"] == "aws:sqs":
                    span_kind = SpanKind.CONSUMER
            except (IndexError, KeyError, TypeError):
                span_kind = SpanKind.SERVER

            tracer = get_tracer(__name__, __version__, tracer_provider)

            with tracer.start_as_current_span(
                    name=orig_handler_name,
                    context=parent_context,
                    kind=span_kind,
            ) as span:
                if span.is_recording():
                    headers = lambda_event.get('headers', {})

                    lambda_http_context = lambda_event.get('requestContext', {}).get('http', None)
                    if lambda_http_context:
                        span.set_attribute(SpanAttributes.HTTP_METHOD, lambda_http_context.get('method', None))
                        span.set_attribute(SpanAttributes.HTTP_SCHEME, lambda_http_context.get('protocol', None))
                        span.set_attribute(SpanAttributes.HTTP_URL, lambda_http_context.get('path', None))
                        span.set_attribute(SpanAttributes.HTTP_TARGET, lambda_http_context.get('path', None))
                        span.set_attribute(SpanAttributes.HTTP_HOST, headers.get('host', None))

                    wrapper_instance.generic_request_handler(headers, lambda_event.get('body', None), span)

                    lambda_context = args[1]
                    # NOTE: The specs mention an exception here, allowing the
                    # `ResourceAttributes.FAAS_ID` attribute to be set as a span
                    # attribute instead of a resource attribute.
                    #
                    # See more:
                    # https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/faas.md#example
                    span.set_attribute(
                        ResourceAttributes.FAAS_ID,
                        lambda_context.invoked_function_arn,
                    )
                    span.set_attribute(
                        SpanAttributes.FAAS_EXECUTION,
                        lambda_context.aws_request_id,
                    )

                result = call_wrapped(*args, **kwargs)
                result_status_code = result.get('statusCode', None)

                if result_status_code:
                    span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, result_status_code)
                wrapper_instance.generic_response_handler(result.get('headers', {}), result.get('body', None), span)
            _tracer_provider = tracer_provider or get_tracer_provider()
            try:
                # NOTE: `force_flush` before function quit in case of Lambda freeze.
                # Assumes we are using the OpenTelemetry SDK implementation of the
                # `TracerProvider`.
                _tracer_provider.force_flush()
            except Exception:  # pylint: disable=broad-except
                logger.error(
                    "TracerProvider was missing `force_flush` method. \
                    This is necessary in case of a Lambda freeze and would exist in the OTel SDK implementation."
                )

            return result

        wrap_function_wrapper(
            wrapped_module_name,
            wrapped_function_name,
            _instrumented_lambda_handler_call,
        )

    def _instrument(self, **kwargs):
        """Instruments Lambda Handlers on AWS Lambda.

        See more:
        https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/instrumentation/aws-lambda.md#instrumenting-aws-lambda

        Args:
            **kwargs: Optional arguments
                ``tracer_provider``: a TracerProvider, defaults to global
                ``event_context_extractor``: a method which takes the Lambda
                    Event as input and extracts an OTel Context from it. By default,
                    the context is extracted from the HTTP headers of an API Gateway
                    request.
        """
        logger.debug("in AwsLambdaInstrumentorWrapper _instrument")
        lambda_handler = os.environ.get(aws_lambda.ORIG_HANDLER, os.environ.get(aws_lambda._HANDLER))  # pylint:disable=W0212
        # pylint: disable=attribute-defined-outside-init
        (
            self._wrapped_module_name,
            self._wrapped_function_name,
        ) = lambda_handler.rsplit(".", 1)

        self._ht_instrument(
            self._wrapped_module_name,
            self._wrapped_function_name,
            event_context_extractor=kwargs.get(
                "event_context_extractor", _default_event_context_extractor
            ),
            tracer_provider=kwargs.get("tracer_provider"),
        )