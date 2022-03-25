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
from concurrent import futures
import re
import sys
import grpc
import json
import traceback

from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.grpc import helloworld_pb2_grpc, helloworld_pb2

logger = setup_custom_logger(__name__)


def test_run(agent_with_filter, exporter):
    agent_with_filter.instrument()
    class Greeter(helloworld_pb2_grpc.GreeterServicer):
        def SayHello(self, request, context):
            logger.debug('Received request.')
            logger.debug('Returning response.')
            return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)


    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50052')
    server.start()


    def exit_callback():
        try:
            with grpc.insecure_channel('0.0.0.0:50052') as channel:
                stub = helloworld_pb2_grpc.GreeterStub(channel)
                permission_denied_exception = False
                try:
                    response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
                except Exception as e:
                    permission_denied_exception = e.args[0].code == grpc.StatusCode.PERMISSION_DENIED

                assert permission_denied_exception

                # Get all of the in memory spans that were recorded for this iteration
                span_list = exporter.get_finished_spans()
                # Confirm something was returned.
                assert span_list

                logger.debug('len(span_list): ' + str(len(span_list)))
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
                assert flaskSpanAsObject['attributes']['rpc.grpc.status_code'] == 7
                exporter.clear()
                return 0
        except:
            logger.error('An error occurred while calling greeter client: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            # raise Exception(sys.exc_info()[0])
            return 1

    logger.info('Starting Test Run.')
    t = threading.Thread(target=exit_callback)
    t.start()
    t.join(4)
