import yaml
import logging

logger = logging.getLogger(__name__)

class HypertraceConfig:  
    DEFAULT_SERVCIE_NAME = "pythonagent"
    DEFAULT_OPA_ENDPOINT = "http://opa.traceableai:8181/";
    DEFAULT_OPA_POLL_PERIOD_SECONDS = 30;
    DEFAULT_BODY_MAX_SIZE_BYTES = 128 * 1024
    REPORTING_ENDPOINT= "http://localhost:9411/api/v2/spans" ;
    REPORTING_SECURE = False ;
    DATA_CAPTURE_HTTP_HEADERS_REQUEST = True ;
    DATA_CAPTURE_HTTP_HEADERS_RESPONSE =  True  ; 
    DATA_CAPTURE_HTTP_BODY_REQUEST = True ;
    DATA_CAPTURE_HTTP_BODY_RESPONSE = True ;
    DATA_CAPTURE_RPC_METADATA_REQUEST = True ;
    DATA_CAPTURE_RPC_METADATA_RESPONSE  = True ;
    DATA_CAPTURE_RPC_BODY_REQUEST = True ;
    DATA_CAPTURE_RPC_BODY_RESPONSE = True ;
    
    def __init__(self):  
      try:
        from configparser import ConfigParser
        with open('agent-config.yaml') as file:
          configs_list = yaml.load(file, Loader=yaml.FullLoader)
          self.DATA_CAPTURE_SERVICE_NAME= configs_list['service_name']
          self.DATA_CAPTURE_HTTP_HEADERS_REQUEST = configs_list['data_capture']['http_headers']['request'];
          self.DATA_CAPTURE_HTTP_HEADERS_RESPONSE = configs_list['data_capture']['http_headers']['response'];
          self.DATA_CAPTURE_HTTP_BODY_REQUEST = configs_list['data_capture']['http_body']['request'];
          self.DATA_CAPTURE_HTTP_BODY_REQUEST = configs_list['data_capture']['http_body']['response'];
          self.DATA_CAPTURE_RPC_METADATA_REQUEST = configs_list['data_capture']['rpc_metadata']['request'];
          self.DATA_CAPTURE_RPC_METADATA_RESPONSE = configs_list['data_capture']['rpc_metadata']['response'];
          self.DATA_CAPTURE_RPC_BODY_REQUEST = configs_list['data_capture']['rpc_body']['request'];
          self.DATA_CAPTURE_RPC_BODY_RESPONSE = configs_list['data_capture']['rpc_body']['response'];
    
      except ImportError:
        logger.error('An error occurred while parsing the agent-config file.')
        from ConfigParser import ConfigParser  # ver. < 3.0

    # getter method 
    def get_DATA_CAPTURE_HTTP_HEADERS_REQUEST(self): 
        return self._DATA_CAPTURE_HTTP_HEADERS_REQUEST 
