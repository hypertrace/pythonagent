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
import threading
import time
from concurrent import futures
import re
import grpc
import json

from tests import setup_custom_logger

from tests.hypertrace.agent.instrumentation.grpc import helloworld_pb2_grpc, helloworld_pb2

logger = setup_custom_logger(__name__)


def test_grpc(agent, exporter):
    agent.instrument()

    class Greeter(helloworld_pb2_grpc.GreeterServicer):
        def SayHello(self, request, context):
            logger.debug('Received request.')
            if request.name != 'no-metadata':
                metadata = (('tester', 'tester'), ('tester2', 'tester2'))
                logger.debug('Setting custom headers.')
                context.set_trailing_metadata(metadata)
            logger.debug('Returning response.')
            return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)


    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.info('Adding GreeterServicer endpoint to server.')
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    logger.info('Adding insecure port.')
    server.add_insecure_port('[::]:50051')
    logger.info('Starting server.')
    server.start()
    logger.info('Waiting for termination.')


    def exit_callback():
        with grpc.insecure_channel('0.0.0.0:50051') as channel:
            stub = helloworld_pb2_grpc.GreeterStub(channel)
            response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
            assert response.message == 'Hello, you!'
            logger.info("Greeter client received: " + response.message)
            # Get all of the in memory spans that were recorded for this iteration
            span_list = exporter.get_finished_spans()
            # Confirm something was returned.
            assert span_list

            logger.debug('len(span_list): ' + str(len(span_list)))
            # 1 span for server + 1 span for client
            assert len(span_list) == 2
            logger.debug('span_list: ' + str(span_list[0].attributes))
            flaskSpanAsObject = json.loads(span_list[0].to_json())

            assert flaskSpanAsObject['attributes']['rpc.system'] == 'grpc'
            assert flaskSpanAsObject['attributes']['rpc.method'] == 'SayHello'
            user_agent_re = re.compile(
                'grpc-python/.* grpc-c/.* (.*; chttp2)')
            assert re.match(
                user_agent_re, flaskSpanAsObject['attributes']['rpc.request.metadata.user-agent'])
            assert flaskSpanAsObject['attributes']['rpc.request.body'] == '{"name": "you"}'
            assert flaskSpanAsObject['attributes']['rpc.grpc.status_code'] == 0
            assert flaskSpanAsObject['attributes']['rpc.response.metadata.tester2'] == 'tester2'
            assert flaskSpanAsObject['attributes']['rpc.response.metadata.tester'] == 'tester'
            assert flaskSpanAsObject['attributes']['rpc.response.body'] == '{"message": "Hello, you!"}'
            exporter.clear()

            stub = helloworld_pb2_grpc.GreeterStub(channel)
            response = stub.SayHello(helloworld_pb2.HelloRequest(name='no-metadata'))
            assert response.message == 'Hello, no-metadata!'
            logger.info("Greeter client received: " + response.message)
            # Get all of the in memory spans that were recorded for this iteration
            span_list = exporter.get_finished_spans()
            # Confirm something was returned.
            assert span_list

            logger.debug('len(span_list): ' + str(len(span_list)))
            # 1 span for server + 1 span for client
            assert len(span_list) == 2
            logger.debug('span_list: ' + str(span_list[0].attributes))
            flaskSpanAsObject = json.loads(span_list[0].to_json())

            assert flaskSpanAsObject['attributes']['rpc.system'] == 'grpc'
            assert flaskSpanAsObject['attributes']['rpc.method'] == 'SayHello'
            user_agent_re = re.compile(
                'grpc-python/.* grpc-c/.* (.*; chttp2)')
            assert re.match(
                user_agent_re, flaskSpanAsObject['attributes']['rpc.request.metadata.user-agent'])
            assert flaskSpanAsObject['attributes']['rpc.request.body'] == '{"name": "no-metadata"}'
            assert flaskSpanAsObject['attributes']['rpc.grpc.status_code'] == 0
            assert flaskSpanAsObject['attributes']['rpc.response.body'] == '{"message": "Hello, no-metadata!"}'
            exporter.clear()



    logger.info('Starting Test Run.')
    t = threading.Thread(target=exit_callback)
    t.start()
    t.join(4)
