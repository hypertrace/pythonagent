'''Base class of all Hypertrace Instrumentation Wrapper classes'''
import sys
import os.path
import inspect
import traceback
import json
import logging
from opentelemetry.trace.span import Span

# Setup logger name
logger = logging.getLogger(__name__)  # pylint: disable=C0103


# This is a base class for all Hypertrace Instrumentation wrapper classes
class BaseInstrumentorWrapper:
    '''This is a base class for all Hypertrace Instrumentation wrapper classes'''
    # Standard extended span attribute names / prefixes
    HTTP_REQUEST_HEADER_PREFIX = 'http.request.header.'
    HTTP_RESPONSE_HEADER_PREFIX = 'http.response.header.'
    HTTP_REQUEST_BODY_PREFIX = 'http.request.body'
    HTTP_RESPONSE_BODY_PREFIX = 'http.response.body'
    RPC_REQUEST_METADATA_PREFIX = 'rpc.request.metadata.'
    RPC_RESPONSE_METADATA_PREFIX = 'rpc.response.metadata.'
    RPC_REQUEST_BODY_PREFIX = 'rpc.request.body'
    RPC_RESPONSE_BODY_PREFIX = 'rpc.response.body'

    # Constructor
    def __init__(self):
        '''constructor'''
        logger.debug('Entering BaseInstrumentorWrapper constructor.')
        super().__init__()
        self._process_request_headers = False
        self._process_response_headers = False
        self._process_request_body = False
        self._process_response_body = False
        self._max_body_size = 128 * 1024

    # Set whether request headers should be put in extended span, takes a BoolValue as input
    def set_process_request_headers(self, process_request_headers) -> None:
        '''Should it process request headers?'''
        logger.debug('Setting self._process_request_headers to \'%s\'',
                     process_request_headers.value)
        self._process_request_headers = process_request_headers

    # Set whether response headers should be put in extended span, takes a BoolValue as input
    def set_process_response_headers(self, process_response_headers) -> None:
        '''Should it process response headers?'''
        logger.debug('Setting self._process_response_headers to \'%s\'',
                     process_response_headers.value)
        self._process_response_headers = process_response_headers

    # Set whether request body should be put in extended span, takes a BoolValue as input
    def set_process_request_body(self, process_request_body) -> None:
        '''should it process request body?'''
        logger.debug('Setting self._process_request_body to \'%s\'',
                     process_request_body.value)
        self._process_request_body = process_request_body

    # Set whether response body should be put in extended span, takes a BoolValue as input
    def set_process_response_body(self, process_response_body) -> None:
        '''should it process response body?'''
        logger.debug('Setting self._process_response_body to \'%s\'',
                     process_response_body.value)
        self._process_response_body = process_response_body

    # Set max body size
    def set_body_max_size(self, max_body_size) -> None:
        '''Set the max body size for this instrumentor.'''
        logger.debug('Setting self.body_max_size to %s.', max_body_size)
        self._max_body_size = max_body_size

    # we need the headers lowercased multiple times
    # just do it once upfront
    def lowercase_headers(self, headers): # pylint:disable=R0201
        '''convert all headers to lowercase'''
        return {k.lower(): v for k, v in headers.items()}

    def add_headers_to_span(self, prefix: str, span: Span, headers: dict): # pylint:disable=R0201
        '''set header attributes on the span'''
        for header_key, header_value in headers.items():
            span.set_attribute(f"{prefix}{header_key}", header_value)

    _ALLOWED_CONTENT_TYPES = [
        "application/json",
        "application/graphql",
        'application/x-www-form-urlencoded'
    ]

    # We need the content type to do some escaping
    # so if we return a content type, that indicates valid for capture,
    # otherwise don't capture
    def eligible_based_on_content_type(self, headers: dict):
        '''find content-type in headers'''
        content_type = headers.get("content-type")
        return content_type if content_type in self._ALLOWED_CONTENT_TYPES else None # plyint:disable=R1710

    def _generic_handler(self, record_headers: bool, header_prefix: str, # pylint:disable=R0913
                         record_body: bool, body_prefix: str,
                         span: Span, headers: dict, body):
        logger.debug('Entering BaseInstrumentationWrapper.generic_handler().')
        try:  # pylint: disable=R1702
            if not span.is_recording():
                return span

            logger.debug('Span is Recording!')
            lowercased_headers = self.lowercase_headers(headers)
            if record_headers:
                self.add_headers_to_span(header_prefix, span, lowercased_headers)

            if record_body:
                content_type = self.eligible_based_on_content_type(lowercased_headers)
                if content_type is None:
                    return span

                body_str = None
                if isinstance(body, bytes):
                    body_str = body.decode('UTF8', 'backslashreplace')
                else:
                    body_str = body

                request_body_str = self.grab_first_n_bytes(body_str)
                if content_type in ['application/json', 'application/graphql']:
                    # why do we need to do this?
                    span.set_attribute(body_prefix, request_body_str.replace("'", '"'))
                else:
                    span.set_attribute(body_prefix, request_body_str)

        except:  # pylint: disable=W0702
            logger.debug('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
        finally:
            return span  # pylint: disable=W0150

    # Generic HTTP Request Handler
    def generic_request_handler(self,  # pylint: disable=R0912
                                request_headers: dict,
                                request_body,
                                span: Span) -> Span:
        '''Add extended request data to the span'''
        logger.debug('Entering BaseInstrumentationWrapper.genericRequestHandler().')
        return self._generic_handler(self._process_request_headers, self.HTTP_REQUEST_HEADER_PREFIX,
                                     self._process_request_body, self.HTTP_REQUEST_BODY_PREFIX,
                                     span, request_headers, request_body)

    # Generic HTTP Response Handler
    def generic_response_handler(self,  # pylint: disable=R0912
                                 response_headers: dict,
                                 response_body,
                                 span: Span) -> Span:  # pylint: disable=R0912
        '''generic response handler'''
        logger.debug(
            'Entering BaseInstrumentationWrapper.genericResponseHandler().')
        return self._generic_handler(self._process_response_headers, self.HTTP_RESPONSE_HEADER_PREFIX,
                                     self._process_response_body, self.HTTP_RESPONSE_BODY_PREFIX,
                                     span, response_headers, response_body)

    # Generic RPC Request Handler
    def generic_rpc_request_handler(self,
                                    request_headers: dict,
                                    request_body,
                                    span: Span) -> Span:
        '''Add extended request rpc data to span.'''
        logger.debug(
            'Entering BaseInstrumentationWrapper.genericRpcRequestHandler().')
        try:
            # Is the span currently recording?
            if not span.is_recording():
                return span

            logger.debug('Span is Recording!')
            lowercased_headers = self.lowercase_headers(request_headers)

            # Log rpc metatdata if requested
            if self._process_request_headers:
                self.add_headers_to_span(self.RPC_REQUEST_METADATA_PREFIX, span, lowercased_headers)
            # Log rpc body if requested
            if self._process_response_body:
                request_body_str = str(request_body)
                request_body_str = self.grab_first_n_bytes(request_body_str)
                span.set_attribute(self.RPC_REQUEST_BODY_PREFIX,
                                   request_body_str)
        except:  # pylint: disable=W0702
            logger.debug('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span  # pylint: disable=W0150

    # Generic RPC Response Handler
    def generic_rpc_response_handler(self,
                                     response_headers: dict,
                                     response_body,
                                     span: Span) -> Span:
        '''Add extended response rpc data to span'''
        logger.debug(
            'Entering BaseInstrumentationWrapper.genericRpcResponseHandler().')
        try:
            # is the span currently recording?
            if not span.is_recording():
                return span

            logger.debug('Span is Recording!')
            lowercased_headers = self.lowercase_headers(response_headers)
            # Log rpc metadata if requested?
            if self._process_response_headers:

                logger.debug('Dumping Response Headers:')
                self.add_headers_to_span(self.RPC_RESPONSE_METADATA_PREFIX, span, lowercased_headers)
            # Log rpc body if requested
            if self._process_response_body:
                response_body_str = str(response_body)
                logger.debug('Processing response body')
                response_body_str = self.grab_first_n_bytes(response_body_str)
                span.set_attribute(
                    self.RPC_RESPONSE_BODY_PREFIX, response_body_str)
        except:  # pylint: disable=W0702
            logger.debug('An error occurred in genericResponseHandler: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span  # pylint: disable=W0150

    # Check body size
    def check_body_size(self, body: str) -> bool:
        '''Is the size of this message body larger than the configured max?'''
        if body in (None, ''):
            return False
        body_len = len(body)
        max_body_size = self._max_body_size
        if max_body_size and body_len > max_body_size:
            logger.debug('message body size is greater than max size.')
            return True
        return False

    # grab first N bytes
    def grab_first_n_bytes(self, body: str) -> str:
        '''Return the first N (max_body_size) bytes of a request'''
        if body in (None, ''):
            return ''
        if self.check_body_size(body):  # pylint: disable=R1705
            return body[0, self._max_body_size]
        else:
            return body
