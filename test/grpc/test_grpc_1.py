# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from concurrent import futures
import sys
import os
import logging
import grpc
import threading
import pytest
from threading import Timer
import traceback
import helloworld_pb2
import helloworld_pb2_grpc
from agent import Agent

def setup_custom_logger(name):
  try:
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('agent.log', mode='a')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
  except:
    logger.error('Failed to customize logger: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())

logger = setup_custom_logger(__name__)

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logger.debug('Received request.')
        metadata = ( ('tester', 'tester'), ('tester2', 'tester2'))
        logger.debug('Setting custom headers.')
        context.set_trailing_metadata(metadata)
        logger.debug('Returning response.')
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)

def serve(timer):
    logger.info('Creating server.')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.info('Adding GreeterServicer endpoint to server.')
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    logger.info('Adding insecure port.')
    server.add_insecure_port('[::]:50051')
    logger.info('Starting server.')
    server.start()
    logger.info('Waiting for termination.') 
    return server
#    server.wait_for_termination()

def exit_callback(): 
  try:
    with grpc.insecure_channel('localhost:50051') as channel:
      stub = helloworld_pb2_grpc.GreeterStub(channel)
      response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    assert response.message == 'Hello, you!'
    logger.info("Greeter client received: " + response.message)
    return 0
  except:
    logger.error('An error occurred while calling greeter client: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())
    return 1

class CustomTimer(Timer):
  def __init__(self, interval, function, args=[], kwargs={}):
    self._original_function = function
    super(CustomTimer, self).__init__(
      interval, self._do_execute, args, kwargs)

  def _do_execute(self, *a, **kw):
    self.result = self._original_function(*a, **kw)

  def join(self):
    logger.info('Waiting for exit_callback() to finish.')
    super(CustomTimer, self).join()
    return self.result

def test_run():
  try:
    #
    # Code snippet here represents the current initialization logic
    #
    logger.info('Initializing agent.')
    agent = Agent()
    agent.registerServerGrpc()
    agent.globalInit()
    logger.info('Agent initialized.')
    #
    # End initialization logic for Python Agent
    #
    logger.info('Starting Test Run.')
    timer = CustomTimer(4.0, exit_callback)
    timer.start()
    server = serve(timer)
    return timer.join()
  except:
    logger.error('An error occurred while calling greeter client: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())
