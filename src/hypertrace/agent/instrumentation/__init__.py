'''Base class of all Hypertrace Instrumentation Wrapper classes'''
import sys
import os.path
import inspect
import traceback
import json
import logging
from opentelemetry.trace.span import Span

# Setup logger name
logger = logging.getLogger(__name__) # pylint: disable=C0103

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
        self._service_name = 'hypertrace-python-agent'
        self._max_body_size = 128 * 1024

    # Dump object for troubleshooting purposes
    def introspect(self, obj) -> None:
        '''Dump object for troubleshooting purposes'''
        logger.debug('Describing object.')
        for func in [type, id, dir, vars, callable]:
            try:
                logger.debug("%s(%s):\t\t%s",
                             func.__name__, self.introspect.__code__.co_varnames[0], func(obj))
                logger.debug("%s: %s",
                             func.__name__, inspect.getmembers(obj))
            except Exception: # pylint: disable=W0703
                logger.error("No data to display")

    def set_process_rules_from_config(self, config) -> None:
        self._process_request_headers = config.agent_config.data_capture.http_headers.request
        self._process_request_body = config.agent_config.data_capture.http_body.request
        self._process_response_headers = config.agent_config.data_capture.http_headers.response
        self._process_response_body = config.agent_config.data_capture.http_body.response
        self._max_body_size = config.agent_config.data_capture.body_max_size_bytes
        self._service_name = config.agent_config.service_name

    # Generic HTTP Request Handler
    def generic_request_handler(self, # pylint: disable=R0912
                                request_headers: tuple,
                                request_body,
                                span: Span) -> Span :
        '''Add extended request data to the span'''
        logger.debug(
            'Entering BaseInstrumentationWrapper.genericRequestHandler().')
        try: # pylint: disable=R1702
            logger.debug('span: %s', str(span))
            # Only log if span is recording.
            if span.is_recording():
                logger.debug('Span is Recording!')
            else:
                return span
            # Log request headers if requested
            if self._process_request_headers:
                logger.debug('Dumping Request Headers:')
                for header in request_headers:
                    logger.debug(str(header))
                    span.set_attribute(
                        self.HTTP_REQUEST_HEADER_PREFIX + header[0].lower(), header[1])
            # Process request body if enabled
            if self._process_request_body:
                # Get content-type value
                content_type_header_tuple = [
                    item for item in request_headers if item[0].lower() == 'content-type']
                logger.debug('content_type_header_tuple=%s',
                             str(content_type_header_tuple))
                # Does the content-type exist?
                if len(content_type_header_tuple) > 0:
                    logger.debug('Found content-type header.')
                    # Does the content-type exist?
                    if content_type_header_tuple[0][1] is not None\
                      and content_type_header_tuple[0][1] != '':
                        logger.debug(
                            'Mimetype/content-type value exists. %s',
                            content_type_header_tuple[0][1])
                        # Is this an interesting content-type?
                        if self.is_interesting_content_type(content_type_header_tuple[0][1]):
                            logger.debug(
                                'This is an interesting content-type.')
                            request_body_str = None
                            if isinstance(request_body, bytes):
                                request_body_str = request_body.decode('UTF8', 'backslashreplace')
                            else:
                                request_body_str = request_body

                            request_body_str = self.grab_first_n_bytes(request_body_str)
                            if content_type_header_tuple[0][1] == 'application/json' \
                              or content_type_header_tuple[0][1] == 'application/graphql':
                                span.set_attribute(self.HTTP_REQUEST_BODY_PREFIX,\
                                  request_body_str.replace("'", '"'))
                            else:
                                span.set_attribute(
                                    self.HTTP_REQUEST_BODY_PREFIX, request_body_str)
        except: # pylint: disable=W0702
            logger.debug('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span # pylint: disable=W0150

    # Generic HTTP Response Handler
    def generic_response_handler(self, # pylint: disable=R0912
                                 response_headers: tuple,
                                 response_body,
                                 span: Span) -> Span: # pylint: disable=R0912
        '''Add extended response data to span.'''
        logger.debug(
            'Entering BaseInstrumentationWrapper.genericResponseHandler().')
        try: # pylint: disable=R1702
            logger.debug('span: %s', str(span))
            # Only log if span is recording.
            if span.is_recording():
                logger.debug('Span is Recording!')
            else:
                return span
            # Log response headers if requested
            if self._process_response_headers:
                logger.debug('Dumping Response Headers:')
                for header in response_headers:
                    logger.debug(str(header))
                    span.set_attribute(
                        self.HTTP_RESPONSE_HEADER_PREFIX + header[0].lower(), header[1])
            # Process response body if enabled
            if self._process_response_body:
                logger.debug('Response Body: %s', str(response_body))
                # Get content-type value
                content_type_header_tuple = [
                    item for item in response_headers if item[0].lower() == 'content-type']
                logger.debug('content_type_header_tuple=%s',
                             str(content_type_header_tuple))
                # Does the content-type exist?
                if len(content_type_header_tuple) > 0:
                    logger.debug('Found content-type header.')
                    # Does the content-type exist?
                    if content_type_header_tuple[0][1] is not None\
                      and content_type_header_tuple[0][1] != '':
                        logger.debug(
                            'Mimetype/content-type value exists. %s',
                            content_type_header_tuple[0][1])
                        # Is this an interesting content-type?
                        if self.is_interesting_content_type(content_type_header_tuple[0][1]):
                            logger.debug(
                                'This is an interesting content-type.')
                            response_body_str = None
                            if isinstance(response_body, bytes):
                                response_body_str = response_body.decode('UTF8', 'backslashreplace')
                            else:
                                response_body_str = response_body

                            response_body_str = self.grab_first_n_bytes(response_body_str)
                            # Format message body correctly
                            if content_type_header_tuple[0][1] == 'application/json'\
                              and content_type_header_tuple[0][1] == 'application/graphql':
                                span.set_attribute(self.HTTP_RESPONSE_BODY_PREFIX,\
                                  response_body_str.replace("'", '"'))
                            else:
                                span.set_attribute(
                                    self.HTTP_RESPONSE_BODY_PREFIX, response_body_str)
        except: # pylint: disable=W0702
            logger.debug('An error occurred in genericResponseHandler: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span # pylint: disable=W0150

    # Should this mimetype be put in the extended span?
    def is_interesting_content_type(self, content_type: str) -> bool: # pylint: disable=R0201
        '''Is this a content-type we want to write to the span?'''
        logger.debug(
            'Entering BaseInstrumentorWrapper.isInterestingContentType().')
        try:
            if content_type == 'application/json':
                return True
            if content_type == 'application/graphql':
                return True
            if content_type == 'application/x-www-form-urlencoded':
                return True
            return False
        except: # pylint: disable=W0702
            logger.debug("""An error occurred while inspecting content-type:
                         exception=%s, stacktrace=%s""",
                         sys.exc_info()[0],
                         traceback.format_exc())
            return False

    # Generic RPC Request Handler
    def generic_rpc_request_handler(self,
                                    request_headers: tuple,
                                    request_body,
                                    span: Span) -> Span:
        '''Add extended request rpc data to span.'''
        logger.debug(
            'Entering BaseInstrumentationWrapper.genericRpcRequestHandler().')
        try:
            logger.debug('span: %s', str(span))
            # Is the span currently recording?
            if span.is_recording():
                logger.debug('Span is Recording!')
            else:
                return span
            # Log rpc metatdata if requested
            if self._process_request_headers:
                logger.debug('Dumping Request Headers:')
                for header in request_headers:
                    logger.debug(str(header))
                    span.set_attribute(
                        self.RPC_REQUEST_METADATA_PREFIX + header[0].lower(), header[1])
            # Log rpc body if requested
            if self._process_request_body:
                request_body_str = str(request_body)
                request_body_str = self.grab_first_n_bytes(request_body_str)
                span.set_attribute(self.RPC_REQUEST_BODY_PREFIX,
                                   request_body_str)
        except: # pylint: disable=W0702
            logger.debug('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span # pylint: disable=W0150

    # Generic RPC Response Handler
    def generic_rpc_response_handler(self,
                                     response_headers: tuple,
                                     response_body,
                                     span: Span) -> Span:
        '''Add extended response rpc data to span'''
        logger.debug(
            'Entering BaseInstrumentationWrapper.genericRpcResponseHandler().')
        try:
            logger.debug('span: %s', str(span))
            logger.debug('responseHeaders: %s', str(response_headers))
            logger.debug('responseBody: %s', str(response_body))
            # is the span currently recording?
            if span.is_recording():
                logger.debug('Span is Recording!')
            else:
                return span
            # Log rpc metadata if requested?
            if self._process_response_headers:
                logger.debug('Dumping Response Headers:')
                for header in response_headers:
                    logger.debug(str(header))
                    span.set_attribute(
                        self.RPC_RESPONSE_METADATA_PREFIX + header[0].lower(), header[1])
            # Log rpc body if requested
            if self._process_response_body:
                response_body_str = str(response_body)
                logger.debug('Processing response body')
                response_body_str = self.grab_first_n_bytes(response_body_str)
                span.set_attribute(
                    self.RPC_RESPONSE_BODY_PREFIX, response_body_str)
        except: # pylint: disable=W0702
            logger.debug('An error occurred in genericResponseHandler: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span # pylint: disable=W0150

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
        if self.check_body_size(body): # pylint: disable=R1705
            return body[0, self._max_body_size]
        else:
            return body
