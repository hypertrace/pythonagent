'''Environment config loader'''

import os
import logging

logger = logging.getLogger(__name__)  # pylint: disable=C0103


def load_config_from_env() -> dict:  # pylint: disable=R0912,R0915
    '''Loads config from environment variables'''
    config = {}

    if 'HT_SERVICE_NAME' in os.environ:
        logger.debug("[env] Loaded HT_SERVICE_NAME from env")
        config['service_name'] = os.environ['HT_SERVICE_NAME']

    # Reporting
    config['reporting'] = {}

    if 'HT_REPORTING_ENDPOINT' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_ENDPOINT from env")
        config['reporting']['endpoint'] = os.environ['HT_REPORTING_ENDPOINT']

    if 'HT_REPORTING_TRACE_REPORTER_TYPE' in os.environ:
        logger.info(
            "[env] Loaded HT_REPORTING_TRACE_REPORTER_TYPE from env")
        config['reporting']['trace_reporter_type'] = \
            os.environ['HT_REPORTING_TRACE_REPORTER_TYPE']

    if 'HT_REPORTING_SECURE' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_SECURE from env")
        config['reporting']['secure'] = os.environ['HT_REPORTING_SECURE'].lower(
        ) == 'true'

    if 'HT_REPORTING_TOKEN' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_TOKEN from env")
        config['reporting']['token'] = os.environ['HT_REPORTING_TOKEN']

    config['reporting']['opa'] = {}

    if 'HT_REPORTING_OPA_ENDPOINT' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_OPA_ENDPOINT from env")
        config['reporting']['opa']['endpoint'] = os.environ['HT_REPORTING_OPA_ENDPOINT']

    if 'HT_REPORTING_OPA_POLL_PERIOD_SECONDS' in os.environ:
        logger.debug(
            "[env] Loaded HT_REPORTING_OPA_POLL_PERIOD_SECONDS from env")
        config['reporting']['opa']['poll_period_seconds'] \
            = int(os.environ['HT_REPORTING_OPA_POLL_PERIOD_SECONDS'])

    if 'HT_REPORTING_OPA_ENABLED' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_OPA_ENABLED from env")
        config['reporting']['opa']['enabled'] \
            = os.environ['HT_REPORTING_OPA_ENABLED'].lower() \
            == 'true'

    if len(config['reporting']['opa']) == 0:
        del config['reporting']['opa']

    if len(config['reporting']) == 0:
        del config['reporting']

    # Data capture
    config['data_capture'] = {}

    config['data_capture']['http_headers'] = {}
    if 'HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST from env")
        config['data_capture']['http_headers']['request'] \
            = os.environ['HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST'].lower() \
            == 'true'

    if 'HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE from env")
        config['data_capture']['http_headers']['response'] \
            = os.environ['HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE'].lower() \
            == 'true'

    if len(config['data_capture']['http_headers']) == 0:
        del config['data_capture']['http_headers']

    config['data_capture']['http_body'] = {}
    if 'HT_DATA_CAPTURE_HTTP_BODY_REQUEST' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_HTTP_BODY_REQUEST from env")
        config['data_capture']['http_body']['request'] \
            = os.environ['HT_DATA_CAPTURE_HTTP_BODY_REQUEST'].lower() \
            == 'true'

    if 'HT_DATA_CAPTURE_HTTP_BODY_RESPONSE' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_HTTP_BODY_RESPONSE from env")
        config['data_capture']['http_body']['response'] \
            = os.environ['HT_DATA_CAPTURE_HTTP_BODY_RESPONSE'].lower() \
            == 'true'

    if len(config['data_capture']['http_body']) == 0:
        del config['data_capture']['http_body']

    config['data_capture']['rpc_metadata'] = {}
    if 'HT_DATA_CAPTURE_RPC_METADATA_REQUEST' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_RPC_METADATA_REQUEST from env")
        config['data_capture']['rpc_metadata']['request'] \
            = os.environ['HT_DATA_CAPTURE_RPC_METADATA_REQUEST'].lower() \
            == 'true'

    if 'HT_DATA_CAPTURE_RPC_METADATA_RESPONSE' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_RPC_METADATA_RESPONSE from env")
        config['data_capture']['rpc_metadata']['response'] \
            = os.environ['HT_DATA_CAPTURE_RPC_METADATA_RESPONSE'].lower() \
            == 'true'

    if len(config['data_capture']['rpc_metadata']) == 0:
        del config['data_capture']['rpc_metadata']

    config['data_capture']['rpc_body'] = {}
    if 'HT_DATA_CAPTURE_RPC_BODY_REQUEST' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_RPC_BODY_REQUEST from env")
        config['data_capture']['rpc_body']['request'] \
            = os.environ['HT_DATA_CAPTURE_RPC_BODY_REQUEST'].lower() \
            == 'true'

    if 'HT_DATA_CAPTURE_RPC_BODY_RESPONSE' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_RPC_BODY_RESPONSE from env")
        config['data_capture']['rpc_body']['response'] \
            = os.environ['HT_DATA_CAPTURE_RPC_BODY_RESPONSE'].lower() \
            == 'true'

    if len(config['data_capture']['rpc_body']) == 0:
        del config['data_capture']['rpc_body']

    if 'HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES' in os.environ:
        logger.debug(
            "[env] Loaded HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES from env")
        config['data_capture']['body_max_size_bytes'] \
            = int(os.environ['HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES'])

    if len(config['data_capture']) == 0:
        del config['data_capture']

    if 'HT_PROPAGATION_FORMATS' in os.environ and len(os.environ['HT_PROPAGATION_FORMATS']) > 0:
        logger.debug("[env] Loaded HT_PROPAGATION_FORMATS from env")
        config['propagation_formats'] = os.environ['HT_PROPAGATION_FORMATS'].split(
            ',')

    if 'HT_ENABLED' in os.environ:
        logger.debug("[env] Loaded HT_ENABLED from env")
        config['enabled'] = os.environ['HT_ENABLED'].lower() == 'true'

    if 'HT_ENABLE_CONSOLE_SPAN_EXPORTER' in os.environ:
        logger.debug("[env] Loaded HT_ENABLE_CONSOLE_SPAN_EXPORTER from env, %s",
                     str(os.environ['HT_ENABLE_CONSOLE_SPAN_EXPORTER'].lower()))
        config['_use_console_span_exporter'] = \
            os.environ['HT_ENABLE_CONSOLE_SPAN_EXPORTER'].lower() == 'true'

    return config
