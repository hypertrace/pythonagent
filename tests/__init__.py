import logging
import os
import sys
import traceback

import pytest

from hypertrace.agent.instrumentation import instrumentation_definitions, logger




os.environ['HT_ENABLE_CONSOLE_SPAN_EXPORTER'] = 'true'


def find_free_port():
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", 0))
    portnum = sock.getsockname()[1]
    sock.close()

    return portnum


def configure_default_environment(agent, config_file_path, service_name):
    os.environ.setdefault('HT_CONFIG_FILE', '')
    os.environ.setdefault('HT_SERVICE_NAME', '')
    os.environ.setdefault('HT_LOG_LEVEL', 'DEBUG')
    os.environ.setdefault('HT_ENABLE_CONSOLE_SPAN_EXPORTER', True)


def configure_inmemory_span_exporter(agent):
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    memoryExporter = InMemorySpanExporter()
    simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
    agent.register_processor(simpleExportSpanProcessor)
    return memoryExporter


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
