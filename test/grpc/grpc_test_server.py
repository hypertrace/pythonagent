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

from __future__ import print_function
from concurrent import futures
import sys
import os
import logging
import grpc
import threading
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
agent.registerGrpc()
agent.globalInit()
logger.info('Agent initialized.')
#
# End initialization logic for Python Agent
#

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        metadata = ( ('tester', 'tester'), ('tester2', 'tester2'))
        context.set_trailing_metadata(metadata)
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
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    print("Greeter client received: " + response.message)
    os._exit(0)

if __name__ == '__main__':
    logger.info('Starting Test Run.')
    timer = threading.Timer(2.0, exit_callback)
    timer.start()
    serve()
