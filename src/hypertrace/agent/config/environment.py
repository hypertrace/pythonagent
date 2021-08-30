'''Environment config loader'''

import logging

from hypertrace.env_var_settings import get_env_value

logger = logging.getLogger(__name__)  # pylint: disable=C0103


def load_config_from_env() -> dict:  # pylint: disable=R0912,R0915,R0914
    '''Loads config from environment variables'''
    config = {}

    service_name = get_env_value('SERVICE_NAME')
    if service_name:
        logger.debug("[env] Loaded SERVICE_NAME from env")
        config['service_name'] = service_name

    # Reporting
    config['reporting'] = {}

    reporting_endpoint = get_env_value('REPORTING_ENDPOINT')
    if reporting_endpoint:
        logger.debug("[env] Loaded REPORTING_ENDPOINT from env")
        config['reporting']['endpoint'] = reporting_endpoint

    reporter_type = get_env_value('REPORTING_TRACE_REPORTER_TYPE')
    if reporter_type:
        logger.info(
            "[env] Loaded REPORTING_TRACE_REPORTER_TYPE from env")
        config['reporting']['trace_reporter_type'] = reporter_type

    reporting_secure = get_env_value('REPORTING_SECURE')
    if reporting_secure:
        logger.debug("[env] Loaded REPORTING_SECURE from env")
        config['reporting']['secure'] = reporting_secure.lower(
        ) == 'true'

    reporting_token = get_env_value('REPORTING_TOKEN')
    if reporting_token:
        logger.debug("[env] Loaded REPORTING_TOKEN from env")
        config['reporting']['token'] = reporting_token

    config['reporting']['opa'] = {}

    reporting_opa_endpoint = get_env_value('REPORTING_OPA_ENDPOINT')
    if reporting_opa_endpoint:
        logger.debug("[env] Loaded REPORTING_OPA_ENDPOINT from env")
        config['reporting']['opa']['endpoint'] = reporting_opa_endpoint

    opa_poll_period = get_env_value('REPORTING_OPA_POLL_PERIOD_SECONDS')
    if opa_poll_period:
        logger.debug(
            "[env] Loaded REPORTING_OPA_POLL_PERIOD_SECONDS from env")
        config['reporting']['opa']['poll_period_seconds'] = int(opa_poll_period)

    opa_enabled = get_env_value('REPORTING_OPA_ENABLED')
    if opa_enabled:
        logger.debug("[env] Loaded REPORTING_OPA_ENABLED from env")
        config['reporting']['opa']['enabled'] = _is_true(opa_enabled)

    if len(config['reporting']['opa']) == 0:
        del config['reporting']['opa']

    if len(config['reporting']) == 0:
        del config['reporting']

    # Data capture
    config['data_capture'] = {}

    config['data_capture']['http_headers'] = {}
    headers_request = get_env_value('DATA_CAPTURE_HTTP_HEADERS_REQUEST')
    if headers_request:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_HTTP_HEADERS_REQUEST from env")
        config['data_capture']['http_headers']['request'] = _is_true(headers_request)

    headers_response = get_env_value('DATA_CAPTURE_HTTP_HEADERS_RESPONSE')
    if headers_response:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_HTTP_HEADERS_RESPONSE from env")
        config['data_capture']['http_headers']['response'] = _is_true(headers_response)

    if len(config['data_capture']['http_headers']) == 0:
        del config['data_capture']['http_headers']

    config['data_capture']['http_body'] = {}
    body_request = get_env_value('DATA_CAPTURE_HTTP_BODY_REQUEST')
    if body_request:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_HTTP_BODY_REQUEST from env")
        config['data_capture']['http_body']['request'] = _is_true(body_request)

    body_response = get_env_value('DATA_CAPTURE_HTTP_BODY_RESPONSE')
    if body_response:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_HTTP_BODY_RESPONSE from env")
        config['data_capture']['http_body']['response'] = _is_true(body_response)

    if len(config['data_capture']['http_body']) == 0:
        del config['data_capture']['http_body']

    config['data_capture']['rpc_metadata'] = {}
    rpc_metadata_request = get_env_value('DATA_CAPTURE_RPC_METADATA_REQUEST')
    if rpc_metadata_request:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_RPC_METADATA_REQUEST from env")
        config['data_capture']['rpc_metadata']['request'] = _is_true(rpc_metadata_request)

    rpc_metadata_response = get_env_value('DATA_CAPTURE_RPC_METADATA_RESPONSE')
    if rpc_metadata_response:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_RPC_METADATA_RESPONSE from env")
        config['data_capture']['rpc_metadata']['response'] = _is_true(rpc_metadata_response)

    if len(config['data_capture']['rpc_metadata']) == 0:
        del config['data_capture']['rpc_metadata']

    config['data_capture']['rpc_body'] = {}
    rpc_body_request = get_env_value('DATA_CAPTURE_RPC_BODY_REQUEST')
    if rpc_body_request:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_RPC_BODY_REQUEST from env")
        config['data_capture']['rpc_body']['request'] = _is_true(rpc_body_request)

    rpc_body_response = get_env_value('DATA_CAPTURE_RPC_BODY_RESPONSE')
    if rpc_body_response:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_RPC_BODY_RESPONSE from env")
        config['data_capture']['rpc_body']['response'] = _is_true(rpc_body_response)

    if len(config['data_capture']['rpc_body']) == 0:
        del config['data_capture']['rpc_body']

    body_max_size_bytes = get_env_value('DATA_CAPTURE_BODY_MAX_SIZE_BYTES')
    if body_max_size_bytes:
        logger.debug(
            "[env] Loaded DATA_CAPTURE_BODY_MAX_SIZE_BYTES from env")
        config['data_capture']['body_max_size_bytes'] = int(body_max_size_bytes)

    if len(config['data_capture']) == 0:
        del config['data_capture']

    propagation_formats = get_env_value('PROPAGATION_FORMATS')
    if propagation_formats and len(propagation_formats) > 0:
        logger.debug("[env] Loaded PROPAGATION_FORMATS from env")
        config['propagation_formats'] = propagation_formats.split(',')

    enabled = get_env_value('ENABLED')
    if enabled:
        logger.debug("[env] Loaded ENABLED from env")
        config['enabled'] = _is_true(enabled)

    console_span_exporter = get_env_value('ENABLE_CONSOLE_SPAN_EXPORTER')
    if console_span_exporter:
        logger.debug("[env] Loaded ENABLE_CONSOLE_SPAN_EXPORTER from env")
        config['_use_console_span_exporter'] = _is_true(console_span_exporter)

    return config

def _is_true(value):
    return value.lower() == 'true'
