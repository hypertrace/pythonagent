import sys
import os.path
import logging
import inspect
import traceback

logger = logging.getLogger(__name__)

class BaseInstrumentorWrapper:

  HTTP_REQUEST_HEADER_PREFIX = 'http.request.header.'
  HTTP_RESPONSE_HEADER_PREFIX = 'http.response.header.'
  HTTP_REQUEST_BODY_PREFIX = 'http.request.body'
  HTTP_RESPONSE_BODY_PREFIX = 'http.response.body'
  RPC_REQUEST_METADATA_PREFIX = 'rpc.request.metadata.'
  RPC_RESPONSE_METADATA_PREFIX = 'rpc.response.metadata.'
  RPC_REQUEST_BODY_PREFIX = 'rpc.request.body'
  RPC_RESPONSE_BODY_PREFIX = 'rpc.response.body'

  def __init__(self):
    logger.debug('Entering BaseInstrumentorWrapper constructor.');
    super().__init__() 
    self._processRequestHeaders = False
    self._processResponseHeaders = False
    self._processRequestBody = False
    self._processResponseBody = False
    self._serviceName = 'hypertrace-python-agent'

  def introspect(self, obj):
    logger.debug('Describing object.')
    for func in [type, id, dir, vars, callable]:
      try:
        logger.debug("%s(%s):\t\t%s" % (func.__name__, self.introspect.__code__.co_varnames[0], func(obj)))
        logger.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
      except Exception:
        logger.error("No data to display");

  def getProcessRequestHeaders(self):
    return self._processRequestHeaders

  def getProcessResponseHeaders(self):
    return self._processResponseHeaders

  def getProcessRequestBody(self):
    return self._processRequestBody

  def getProcessResponseBody(self):
    return self._processResponseBody

  def getServiceName(self):
    return self._serviceName

  def setProcessRequestHeaders(self, processRequestHeaders):
    logger.debug('Setting self._processRequestHeaders.')
    self._processRequestHeaders = processRequestHeaders

  def setProcessResponseHeaders(self, processResponseHeaders):
    logger.debug('Setting self._processResponseHeaders.');
    self._processResponseHeaders = processResponseHeaders

  def setProcessRequestBody(self, processRequestBody):
    logger.debug('Setting self._processRequestBody.');
    self._processRequestBody = processRequestBody

  def setProcessResponseBody(self, processResponseBody):
    logger.debug('Setting self._processResponseBody.');
    self._processResponseBody = processResponseBody

  def setServiceName(self, serviceName):
    logger.debug('Setting self._serviceName')
    self._serviceName = serviceName

  def genericRequestHandler(self, requestHeaders, requestBody, span):
    logger.debug('Entering BaseInstrumentationWrapper.genericRequestHandler().');
    try:
      logger.debug('span: ' + str(span))
      logger.debug('requestHeaders: ' + str(requestHeaders))
      logger.debug('requestBody: ' + str(requestBody))
      if span.is_recording():
        logger.debug('Span is Recording!')
      else:
        return span
      if self.getProcessRequestHeaders():
        logger.debug('Dumping Request Headers:')
        for h in requestHeaders:
          logger.debug(str(h))
          span.set_attribute(self.HTTP_REQUEST_HEADER_PREFIX + h[0].lower(), h[1])
      if self.getProcessRequestBody():
        logger.debug('Request Body: ' + str(requestBody))
        contentTypeHeaderTuple = [item for item in requestHeaders if item[0].lower() == 'content-type']
        logger.debug('contentTypeHeaderTuple=' + str(contentTypeHeaderTuple))
        if len(contentTypeHeaderTuple) > 0:
          logger.debug('Found content-type header.')
          if contentTypeHeaderTuple[0][1] != None and contentTypeHeaderTuple[0][1] != '':
            logger.debug('Mimetype/content-type value exists. %s', contentTypeHeaderTuple[0][1])
            if self.isInterestingContentType(contentTypeHeaderTuple[0][1]):
              logger.debug('This is an interesting content-type.')
              if contentTypeHeaderTuple[0][1] == 'application/json':
                span.set_attribute(self.HTTP_REQUEST_BODY_PREFIX, json.dumps(json.loads(requestBody.decode('UTF8').replace("'", '"'))))
              else:
                span.set_attribute(self.HTTP_REQUEST_BODY_PREFIX, str(requestBody.decode('UTF8')))
    except:
      logger.error('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.

  def genericResponseHandler(self, responseHeaders, responseBody, span):
    logger.debug('Entering BaseInstrumentationWrapper.genericResponseHandler().');
    try:
      logger.debug('span: ' + str(span))
      logger.debug('responseHeaders: ' + str(responseHeaders))
      logger.debug('responseBody: ' + str(responseBody))
      if span.is_recording():
        logger.debug('Span is Recording!')
      else:
        return span
      if self.getProcessResponseHeaders():
        logger.debug('Dumping Response Headers:')
        for h in responseHeaders:
          logger.debug(str(h))
          span.set_attribute(self.HTTP_RESPONSE_HEADER_PREFIX + h[0].lower(), h[1])
      if self.getProcessResponseBody():
        logger.debug('Response Body: ' + str(responseBody))
        contentTypeHeaderTuple = [item for item in responseHeaders if item[0].lower() == 'content-type']
        logger.debug('contentTypeHeaderTuple=' + str(contentTypeHeaderTuple))
        if len(contentTypeHeaderTuple) > 0:
          logger.debug('Found content-type header.')
          if contentTypeHeaderTuple[0][1] != None and contentTypeHeaderTuple[0][1] != '':
            logger.debug('Mimetype/content-type value exists. %s', contentTypeHeaderTuple[0][1])
            if self.isInterestingContentType(contentTypeHeaderTuple[0][1]):
              logger.debug('This is an interesting content-type.')
              if contentTypeHeaderTuple[0][1] == 'application/json':
                span.set_attribute(self.HTTP_RESPONSE_BODY_PREFIX, json.dumps(json.loads(responseBody.decode('UTF8').replace("'", '"'))))
              else:
                span.set_attribute(self.HTTP_RESPONSE_BODY_PREFIX, str(responseBody.decode('UTF8')))
    except:
      logger.error('An error occurred in genericResponseHandler: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.

  def isInterestingContentType(self, contentType):
    logger.debug('Entering FlaskInstrumentorWrapper.isInterestingContentType().')
    try:
      if contentType == 'application/json': return True
      if contentType == 'application/graphql': return True
      if contentType == 'application/x-www-form-urlencoded': return True
      return False;
    except:
      logger.error('An error occurred while inspecting content-type: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      return False

  def genericRpcRequestHandler(self, requestHeaders, requestBody, span):
    logger.debug('Entering BaseInstrumentationWrapper.genericRpcRequestHandler().');
    try:
      logger.debug('span: ' + str(span))
      logger.debug('requestHeaders: ' + str(requestHeaders))
      logger.debug('requestBody: ' + str(requestBody))
      if span.is_recording():
        logger.debug('Span is Recording!')
      else:
        return span
      if self.getProcessRequestHeaders():
        logger.debug('Dumping Request Headers:')
        for h in requestHeaders:
          logger.debug(str(h))
          span.set_attribute(self.RPC_REQUEST_METADATA_PREFIX + h[0].lower(), h[1])
      if self.getProcessRequestBody():
        logger.debug('Request Body: ' + str(requestBody))
        span.set_attribute(self.RPC_REQUEST_BODY_PREFIX, str(requestBody))
    except:
      logger.error('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.

  def genericRpcResponseHandler(self, responseHeaders, responseBody, span):
    logger.debug('Entering BaseInstrumentationWrapper.genericRpcResponseHandler().');
    try:
      logger.debug('span: ' + str(span))
      logger.debug('responseHeaders: ' + str(responseHeaders))
      logger.debug('responseBody: ' + str(responseBody))
      if span.is_recording():
        logger.debug('Span is Recording!')
      else:
        return span
      if self.getProcessResponseHeaders():
        logger.debug('Dumping Response Headers:')
        for h in responseHeaders:
          logger.debug(str(h))
          span.set_attribute(self.RPC_RESPONSE_METADATA_PREFIX + h[0].lower(), h[1])
      if self.getProcessResponseBody():
        logger.debug('Response Body: ' + str(responseBody))
        span.set_attribute(self.RPC_RESPONSE_BODY_PREFIX, str(responseBody))
    except:
      logger.error('An error occurred in genericResponseHandler: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.
