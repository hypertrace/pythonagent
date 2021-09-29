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
import re
import sys
import os
import logging
import grpc
import threading
import pytest
import json
from threading import Timer
import traceback
import helloworld_pb2
import helloworld_pb2_grpc
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export, Span
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from hypertrace.agent import Agent
from hypertrace.agent.filter import Filter
from hypertrace.agent.filter.registry import Registry


class SampleBlockingFilter(Filter):

    def evaluate_url_and_headers(self, span: Span, url: str, headers: tuple) -> bool:
        return True

    def evaluate_body(self, span: Span, body) -> bool:
        pass



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

#
# Code snippet here represents the current initialization logic
#
logger.info('Initializing agent.')
agent = Agent()
registry = Registry().register(SampleBlockingFilter)

agent.instrument()
logger.info('Agent initialized.')
#
# End initialization logic for Python Agent
#

# Setup In-Memory Span Exporter
logger.info('Agent initialized.')
logger.info('Adding in-memory span exporter.')
memoryExporter = InMemorySpanExporter()
simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
agent.register_processor(simpleExportSpanProcessor)

logger.info('Added in-memoy span exporter')


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logger.debug('Received request.')
        metadata = (('tester', 'tester'), ('tester2', 'tester2'))
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


def exit_callback():
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = helloworld_pb2_grpc.GreeterStub(channel)
            permission_denied_exception = False
            try:
                response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
            except Exception as e:
                permission_denied_exception = e.args[0].code == grpc.StatusCode.PERMISSION_DENIED

            assert permission_denied_exception

            # Get all of the in memory spans that were recorded for this iteration
            span_list = memoryExporter.get_finished_spans()
            # Confirm something was returned.
            assert span_list
            # Confirm there are three spans
            logger.debug('len(span_list): ' + str(len(span_list)))
            assert len(span_list) == 1
            logger.debug('span_list: ' + str(span_list[0].attributes))
            flaskSpanAsObject = json.loads(span_list[0].to_json())

            assert flaskSpanAsObject['attributes']['rpc.system'] == 'grpc'
            assert flaskSpanAsObject['attributes']['rpc.method'] == 'SayHello'
            user_agent_re = re.compile(
                'grpc-python/.* grpc-c/.* (.*; chttp2)')
            assert re.match(
                user_agent_re, flaskSpanAsObject['attributes']['rpc.request.metadata.user-agent'])
            assert flaskSpanAsObject['attributes']['rpc.request.body'] == 'name: \"you\"\n'
            assert flaskSpanAsObject['attributes']['rpc.grpc.status_code'] == 7
            memoryExporter.clear()
            return 0
    except:
        logger.error('An error occurred while calling greeter client: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        # raise Exception(sys.exc_info()[0])
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
        logger.info('Starting Test Run.')
        timer = CustomTimer(4.0, exit_callback)
        timer.start()
        server = serve(timer)
        rc = timer.join()
        if rc == 1:
            raise Exception('Test failed.')
    except:
        logger.error('An error occurred while calling greeter client: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        raise sys.exc_info()[0]
