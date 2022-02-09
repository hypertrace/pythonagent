import sys
import logging
import traceback

from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from hypertrace.agent import Agent

import io
import json
import sys
import zipfile

import botocore.session
from moto import mock_iam, mock_lambda  # pylint: disable=import-error


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
        print('Failed to customize logger: exception=%s, stacktrace=%s',
              sys.exc_info()[0],
              traceback.format_exc())

@mock_iam
def test_run():
    logger = setup_custom_logger(__name__)
    agent = Agent()
    agent.instrument(None)

    # Setup In-Memory Span Exporter
    logger.info('Agent initialized.')
    logger.info('Adding in-memory span exporter.')
    memoryExporter = InMemorySpanExporter()
    simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
    agent.register_processor(simpleExportSpanProcessor)
    logger.info('Added in-memory span exporter')

    logger.info('Running test calls.')
    try:
        session = botocore.session.get_session()
        session.set_credentials(
            access_key="access-key", secret_key="secret-key"
        )
        region = "us-west-2"
        client = session.create_client("lambda", region_name=region)
        iam_client = session.create_client("iam", region_name=region)
        arn = _create_role_and_get_arn(iam_client)
        result = _create_lambda_function(
            'some_function', return_headers_lambda_str(), client, arn
        )
        memoryExporter.clear()
        response = client.invoke(
            Payload=json.dumps({}),
            FunctionName=result['FunctionArn'],
            InvocationType="RequestResponse",
        )

        spans = memoryExporter.get_finished_spans()
        invoke_span = spans[-1]

        assert invoke_span.attributes['faas.invoked_name'] == 'some_function'
        assert invoke_span.attributes['http.status_code'] == '200'
        assert invoke_span.attributes['rpc.service'] == 'Lambda'
        memoryExporter.clear()

        return 0
    except:
        logger.error('Failed to test boto instrumentation wrapper: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        raise sys.exc_info()[0]


def get_as_zip_file(file_name, content):
    zip_output = io.BytesIO()
    with zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(file_name, content)
    zip_output.seek(0)
    return zip_output.read()


def return_headers_lambda_str():
    pfunc = """
def lambda_handler(event, context):
    print("custom log event")
    headers = event.get('headers', event.get('attributes', {}))
    return headers
"""
    return pfunc



@mock_iam
def _create_role_and_get_arn(iam_client) -> str:
    return iam_client.create_role(
        RoleName="my-role",
        AssumeRolePolicyDocument="some policy",
        Path="/my-path/",
    )["Role"]["Arn"]

@mock_lambda
def _create_lambda_function(function_name: str, function_code: str, client, role_arn):
    return client.create_function(
        FunctionName=function_name,
        Runtime="python3.8",
        Role=role_arn,
        Handler="lambda_function.lambda_handler",
        Code={
            "ZipFile": get_as_zip_file("lambda_function.py", function_code)
        },
        Description="test lambda function",
        Timeout=3,
        MemorySize=128,
        Publish=True,
    )

