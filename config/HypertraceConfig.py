
DEFAULT_REPORTING_ENDPOINT = "http://localhost:9411/api/v2/spans";
DEFAULT_OPA_ENDPOINT = "http://opa.traceableai:8181/";
DEFAULT_OPA_POLL_PERIOD_SECONDS = 30;
DEFAULT_BODY_MAX_SIZE_BYTES = 128 * 1024

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

# instantiate
config = ConfigParser()

# parse existing file
config.read('agent.ini')

# read values from a section
string_val = config.get('agent', 'service_name')

print ("dump config :"+ string_val);
