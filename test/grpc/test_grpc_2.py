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
import traceback
import helloworld_pb2
import helloworld_pb2_grpc
from agent import Agent

logging.basicConfig(filename='agent.log', level=logging.DEBUG,)
logger = logging.getLogger(__name__)

#
# Code snippet here represents the current initialization logic
#
logger.info('Initializing agent.')
agent = Agent()
agent.registerClientGrpc()
agent.globalInit()
logger.info('Agent initialized.')
#
# End initialization logic for Python Agent
#

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logger.debug('Received request.')
        metadata = ( ('tester3', 'tester3'), ('tester4', 'tester4'))
        logger.debug('Setting custom headers.')
        context.set_trailing_metadata(metadata)
        logger.debug('Returning response.')
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)

def serve():
    logger.info('Creating server.')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.info('Adding GreeterServicer endpoint to server.')
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    logger.info('Adding insecure port.')
    server.add_insecure_port('[::]:50051')
    logger.info('Starting server.')
    server.start()
    logger.info('Waiting for termination.') 
    server.wait_for_termination()

def exit_callback(): 
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    try:
      with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        metadata = (('tester1', 'tester1'),
                    ('tester2', 'tester2'))
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'), metadata=metadata)
        logger.info("Greeter client received: " + response.message)
        os._exit(0)
    except:
      logger.error('An error occurred while calling greeter client: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      os._exit(1)

def test_run():
  logger.info('Starting Test Run.')
  timer = threading.Timer(4.0, exit_callback)
  timer.start()
  serve()
