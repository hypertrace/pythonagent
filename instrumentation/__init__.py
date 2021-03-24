import sys
import os.path
import logging
import inspect
import traceback
import json

# Setup logger name
logger = logging.getLogger(__name__)

# This is a base class for all Hypertrace Instrumentation wrapper classes
class BaseInstrumentorWrapper:
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
    logger.debug('Entering BaseInstrumentorWrapper constructor.');
    super().__init__() 
    self._processRequestHeaders = False
    self._processResponseHeaders = False
    self._processRequestBody = False
    self._processResponseBody = False
    self._serviceName = 'hypertrace-python-agent'

  # Dump object for troubleshooting purposes
  def introspect(self, obj):
    logger.debug('Describing object.')
    for func in [type, id, dir, vars, callable]:
      try:
        logger.debug("%s(%s):\t\t%s" % (func.__name__, self.introspect.__code__.co_varnames[0], func(obj)))
        logger.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
      except Exception:
        logger.error("No data to display");

  # Log request headers in extended options?
  def getProcessRequestHeaders(self):
    return self._processRequestHeaders

  # Log response headers in extended options?
  def getProcessResponseHeaders(self):
    return self._processResponseHeaders

  # Log request body in extended options?
  def getProcessRequestBody(self):
    return self._processRequestBody

  # Log response body in extended options?
  def getProcessResponseBody(self):
    return self._processResponseBody

  # Get the configured service name
  def getServiceName(self):
    return self._serviceName

  # Set whether request headers should be put in extended span
  def setProcessRequestHeaders(self, processRequestHeaders):
    logger.debug('Setting self._processRequestHeaders.')
    self._processRequestHeaders = processRequestHeaders

  # Set whether response headers should be put in extended span
  def setProcessResponseHeaders(self, processResponseHeaders):
    logger.debug('Setting self._processResponseHeaders.');
    self._processResponseHeaders = processResponseHeaders

  # Set whether request body should be put in extended span
  def setProcessRequestBody(self, processRequestBody):
    logger.debug('Setting self._processRequestBody.');
    self._processRequestBody = processRequestBody

  # Set whether response body should be put in extended span
  def setProcessResponseBody(self, processResponseBody):
    logger.debug('Setting self._processResponseBody.');
    self._processResponseBody = processResponseBody

  # Set service name
  def setServiceName(self, serviceName):
    logger.debug('Setting self._serviceName')
    self._serviceName = serviceName

  # Generic HTTP Request Handler
  def genericRequestHandler(self, requestHeaders, requestBody, span):
    logger.debug('Entering BaseInstrumentationWrapper.genericRequestHandler().');
    try:
      logger.debug('span: ' + str(span))
      logger.debug('requestHeaders: ' + str(requestHeaders))
      logger.debug('requestBody: ' + str(requestBody))
      # Only log if span is recording.
      if span.is_recording():
        logger.debug('Span is Recording!')
      else:
        return span
      # Log request headers if requested
      if self.getProcessRequestHeaders():
        logger.debug('Dumping Request Headers:')
        for h in requestHeaders:
          logger.debug(str(h))
          span.set_attribute(self.HTTP_REQUEST_HEADER_PREFIX + h[0].lower(), h[1])
      # Log request body if requested
      if self.getProcessRequestBody():
        logger.debug('Request Body: ' + str(requestBody))
        # Get content-type value
        contentTypeHeaderTuple = [item for item in requestHeaders if item[0].lower() == 'content-type']
        logger.debug('contentTypeHeaderTuple=' + str(contentTypeHeaderTuple))
        # Does the content-type exist?
        if len(contentTypeHeaderTuple) > 0:
          logger.debug('Found content-type header.')
          # Does the content-type exist?
          if contentTypeHeaderTuple[0][1] != None and contentTypeHeaderTuple[0][1] != '':
            logger.debug('Mimetype/content-type value exists. %s', contentTypeHeaderTuple[0][1])
            # Is this an interesting content-type?
            if self.isInterestingContentType(contentTypeHeaderTuple[0][1]):
              logger.debug('This is an interesting content-type.')
              if contentTypeHeaderTuple[0][1] == 'application/json' or contentTypeHeaderTuple[0][1] == 'application/graphql':
                logger.info('RCBJ0500: ' + requestBody.decode('UTF8'))
                span.set_attribute(self.HTTP_REQUEST_BODY_PREFIX,
                  json.dumps(json.loads(requestBody.decode('UTF8').replace("'", '"'))))
              else:
                span.set_attribute(self.HTTP_REQUEST_BODY_PREFIX,
                  str(requestBody.decode('UTF8')))
    except:
      logger.error('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.

  # Generic HTTP Response Handler
  def genericResponseHandler(self, responseHeaders, responseBody, span):
    logger.debug('Entering BaseInstrumentationWrapper.genericResponseHandler().');
    try:
      logger.debug('span: ' + str(span))
      logger.debug('responseHeaders: ' + str(responseHeaders))
      logger.debug('responseBody: ' + str(responseBody))
      # Only log if span is recording.
      if span.is_recording():
        logger.debug('Span is Recording!')
      else:
        return span
      # Log response headers if requested
      if self.getProcessResponseHeaders():
        logger.debug('Dumping Response Headers:')
        for h in responseHeaders:
          logger.debug(str(h))
          span.set_attribute(self.HTTP_RESPONSE_HEADER_PREFIX + h[0].lower(), h[1])
      # Log response body if requesed
      if self.getProcessResponseBody():
        logger.debug('Response Body: ' + str(responseBody))
        # Get content-type value
        contentTypeHeaderTuple = [item for item in responseHeaders if item[0].lower() == 'content-type']
        logger.debug('contentTypeHeaderTuple=' + str(contentTypeHeaderTuple))
        # Does the content-type exist?
        if len(contentTypeHeaderTuple) > 0:
          logger.debug('Found content-type header.')
          # Does the content-type exist?
          if contentTypeHeaderTuple[0][1] != None and contentTypeHeaderTuple[0][1] != '':
            logger.debug('Mimetype/content-type value exists. %s', contentTypeHeaderTuple[0][1])
            # Is this an interesting content-type?
            if self.isInterestingContentType(contentTypeHeaderTuple[0][1]):
              logger.debug('This is an interesting content-type.')
              # Format message body correctly
              if contentTypeHeaderTuple[0][1] == 'application/json' and contentTypeHeaderTuple[0][1] == 'application/graphql':
                span.set_attribute(self.HTTP_RESPONSE_BODY_PREFIX,
                  json.dumps(json.loads(responseBody.decode('UTF8').replace("'", '"'))))
              else:
                span.set_attribute(self.HTTP_RESPONSE_BODY_PREFIX,
                  str(responseBody.decode('UTF8')))
    except:
      logger.error('An error occurred in genericResponseHandler: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.

  # Should this mimetype be put in the extended span?
  def isInterestingContentType(self, contentType):
    logger.debug('Entering FlaskInstrumentorWrapper.isInterestingContentType().')
    try:
      if contentType == 'application/json': return True
      if contentType == 'application/graphql': return True
      if contentType == 'application/x-www-form-urlencoded': return True
      return False;
    except:
      logger.error('An error occurred while inspecting content-type: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      return False

  # Generic RPC Request Handler
  def genericRpcRequestHandler(self, requestHeaders, requestBody, span):
    logger.debug('Entering BaseInstrumentationWrapper.genericRpcRequestHandler().');
    try:
      logger.debug('span: ' + str(span))
      logger.debug('requestHeaders: ' + str(requestHeaders))
      logger.debug('requestBody: ' + str(requestBody))
      # Is the span currently recording?
      if span.is_recording():
        logger.debug('Span is Recording!')
      else:
        return span
      # Log rpc metatdata if requested
      if self.getProcessRequestHeaders():
        logger.debug('Dumping Request Headers:')
        for h in requestHeaders:
          logger.debug(str(h))
          span.set_attribute(self.RPC_REQUEST_METADATA_PREFIX + h[0].lower(), h[1])
      # Log rpc body if requested
      if self.getProcessRequestBody():
        logger.debug('Request Body: ' + str(requestBody))
        span.set_attribute(self.RPC_REQUEST_BODY_PREFIX, 
          str(requestBody))
    except:
      logger.error('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.

  # Generic RPC Response Handler
  def genericRpcResponseHandler(self, responseHeaders, responseBody, span):
    logger.debug('Entering BaseInstrumentationWrapper.genericRpcResponseHandler().');
    try:
      logger.debug('span: ' + str(span))
      logger.debug('responseHeaders: ' + str(responseHeaders))
      logger.debug('responseBody: ' + str(responseBody))
      # is the span currently recording?
      if span.is_recording():
        logger.debug('Span is Recording!')
      else:
        return span
      # Log rpc metadata if requested?
      if self.getProcessResponseHeaders():
        logger.debug('Dumping Response Headers:')
        for h in responseHeaders:
          logger.debug(str(h))
          span.set_attribute(self.RPC_RESPONSE_METADATA_PREFIX + h[0].lower(), h[1])
      # Log rpc body if requested
      if self.getProcessResponseBody():
        logger.debug('Response Body: ' + str(responseBody))
        span.set_attribute(self.RPC_RESPONSE_BODY_PREFIX, str(responseBody))
    except:
      logger.error('An error occurred in genericResponseHandler: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.
