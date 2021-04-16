import config_pb2 as config_pb2

import logging

logger = logging.getLogger(__name__)

class AgentConfig: 

    AGENT_CONFIG_NAME = '' 
    AGENT_CONFIG_FULL_NAME = '' 
    AGENT_CONFIG_FILE = ''
    AGENT_CONFIG_FILE_NAME = ''
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



#Agent Config 
agent_config  = config_pb2._AGENTCONFIG
print(agent_config.name)
print(agent_config.full_name)
print(agent_config.file)
print(agent_config.containing_type)
agent_config_list = [field.name for field in agent_config.fields]
print("**** Agent Config  fields ****")
for i in range(len(agent_config_list)): 
    print(agent_config_list[i])

#Following attributes need to be set 
agent_config  = config_pb2.AgentConfig()
agent_config.data_capture.http_headers = 'false';
agent_config.reporting.endpoint = "https://test"


# DataCapture describes the elements to be captured by the agent instrumentation
data_capture = config_pb2._DATACAPTURE
res = [field.name for field in data_capture.fields]
if 'http_headers' in str(res):
     DATA_CAPTURE_HTTP_HEADERS_REQUEST=True
if 'http_headers' in str(res):
     DATA_CAPTURE_HTTP_HEADERS_REQUEST=True
if 'http_body' in str(res):
     DATA_CAPTURE_HTTP_BODY_REQUEST=True
if 'http_body' in str(res):
     DATA_CAPTURE_HTTP_BODY_RESPONSE=True
print("****DataCapture fields****")
for i in range(len(res)): 
    print(res[i])


#Reporting
reporting = config_pb2._REPORTING
reporting_list = [field.name for field in reporting.fields]
print("**** Reporting  fields ****")
for i in range(len(reporting_list)): 
    print(reporting_list[i])



#TraceReporterType represents the reporting format for trace data.
trace_reportertype = config_pb2._TRACEREPORTERTYPE 
trace_reportertype_list = [field.name for field in trace_reportertype.fields]
print("**** Report Type fields ****")
for i in range(len(trace_reportertype_list)): 
    print(trace_reportertype_list[i])
