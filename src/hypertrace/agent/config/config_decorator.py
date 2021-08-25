from hypertrace.agent.config import DEFAULT_AGENT_CONFIG

# When we expose the config customization to end users
# rather than have them interact directly with protobuf object they can use this
# which then has modified fields copied to internal agent config
class ConfigDecorator():
    def generate_wrapper(self, copy_from, copy_to):
        for k, v in copy_from.items():
            if isinstance(v, dict):
                self.generate_wrapper(copy_from, copy_to)
            else:
                copy_to[k] = None

    def __init__(self):
        _wrapped = {}
        self.generate_wrapper(DEFAULT_AGENT_CONFIG, _wrapped)