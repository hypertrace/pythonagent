# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: config.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='config.proto',
  package='hypertrace.agent.config.v1',
  syntax='proto3',
  serialized_options=b'\n\036org.hypertrace.agent.config.v1Z,github.com/hypertrace/agent-config/gen/go/v1',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0c\x63onfig.proto\x12\x1ahypertrace.agent.config.v1\x1a\x1egoogle/protobuf/wrappers.proto\"\x86\x04\n\x0b\x41gentConfig\x12\x32\n\x0cservice_name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x38\n\treporting\x18\x02 \x01(\x0b\x32%.hypertrace.agent.config.v1.Reporting\x12=\n\x0c\x64\x61ta_capture\x18\x03 \x01(\x0b\x32\'.hypertrace.agent.config.v1.DataCapture\x12J\n\x13propagation_formats\x18\x04 \x03(\x0e\x32-.hypertrace.agent.config.v1.PropagationFormat\x12+\n\x07\x65nabled\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x38\n\tjavaagent\x18\x06 \x01(\x0b\x32%.hypertrace.agent.config.v1.JavaAgent\x12\\\n\x13resource_attributes\x18\x07 \x03(\x0b\x32?.hypertrace.agent.config.v1.AgentConfig.ResourceAttributesEntry\x1a\x39\n\x17ResourceAttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x96\x03\n\tReporting\x12.\n\x08\x65ndpoint\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\x06secure\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12+\n\x05token\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12J\n\x13trace_reporter_type\x18\x05 \x01(\x0e\x32-.hypertrace.agent.config.v1.TraceReporterType\x12/\n\tcert_file\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x35\n\x0fmetric_endpoint\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12L\n\x14metric_reporter_type\x18\x08 \x01(\x0e\x32..hypertrace.agent.config.v1.MetricReporterType\"d\n\x07Message\x12+\n\x07request\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12,\n\x08response\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\xf1\x02\n\x0b\x44\x61taCapture\x12\x39\n\x0chttp_headers\x18\x01 \x01(\x0b\x32#.hypertrace.agent.config.v1.Message\x12\x36\n\thttp_body\x18\x02 \x01(\x0b\x32#.hypertrace.agent.config.v1.Message\x12\x39\n\x0crpc_metadata\x18\x03 \x01(\x0b\x32#.hypertrace.agent.config.v1.Message\x12\x35\n\x08rpc_body\x18\x04 \x01(\x0b\x32#.hypertrace.agent.config.v1.Message\x12\x38\n\x13\x62ody_max_size_bytes\x18\x05 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12\x43\n\x1e\x62ody_max_processing_size_bytes\x18\x06 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\"C\n\tJavaAgent\x12\x36\n\x10\x66ilter_jar_paths\x18\x01 \x03(\x0b\x32\x1c.google.protobuf.StringValue*-\n\x11PropagationFormat\x12\x06\n\x02\x42\x33\x10\x00\x12\x10\n\x0cTRACECONTEXT\x10\x01*`\n\x11TraceReporterType\x12\x0f\n\x0bUNSPECIFIED\x10\x00\x12\n\n\x06ZIPKIN\x10\x01\x12\x08\n\x04OTLP\x10\x02\x12\x0b\n\x07LOGGING\x10\x03\x12\x08\n\x04NONE\x10\x04\x12\r\n\tOTLP_HTTP\x10\x05*\xbf\x01\n\x12MetricReporterType\x12$\n METRIC_REPORTER_TYPE_UNSPECIFIED\x10\x00\x12\x1d\n\x19METRIC_REPORTER_TYPE_OTLP\x10\x01\x12#\n\x1fMETRIC_REPORTER_TYPE_PROMETHEUS\x10\x02\x12 \n\x1cMETRIC_REPORTER_TYPE_LOGGING\x10\x03\x12\x1d\n\x19METRIC_REPORTER_TYPE_NONE\x10\x04\x42N\n\x1eorg.hypertrace.agent.config.v1Z,github.com/hypertrace/agent-config/gen/go/v1b\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_wrappers__pb2.DESCRIPTOR,])

_PROPAGATIONFORMAT = _descriptor.EnumDescriptor(
  name='PropagationFormat',
  full_name='hypertrace.agent.config.v1.PropagationFormat',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='B3', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TRACECONTEXT', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1549,
  serialized_end=1594,
)
_sym_db.RegisterEnumDescriptor(_PROPAGATIONFORMAT)

PropagationFormat = enum_type_wrapper.EnumTypeWrapper(_PROPAGATIONFORMAT)
_TRACEREPORTERTYPE = _descriptor.EnumDescriptor(
  name='TraceReporterType',
  full_name='hypertrace.agent.config.v1.TraceReporterType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='ZIPKIN', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='OTLP', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='LOGGING', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='NONE', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='OTLP_HTTP', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1596,
  serialized_end=1692,
)
_sym_db.RegisterEnumDescriptor(_TRACEREPORTERTYPE)

TraceReporterType = enum_type_wrapper.EnumTypeWrapper(_TRACEREPORTERTYPE)
_METRICREPORTERTYPE = _descriptor.EnumDescriptor(
  name='MetricReporterType',
  full_name='hypertrace.agent.config.v1.MetricReporterType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='METRIC_REPORTER_TYPE_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='METRIC_REPORTER_TYPE_OTLP', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='METRIC_REPORTER_TYPE_PROMETHEUS', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='METRIC_REPORTER_TYPE_LOGGING', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='METRIC_REPORTER_TYPE_NONE', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1695,
  serialized_end=1886,
)
_sym_db.RegisterEnumDescriptor(_METRICREPORTERTYPE)

MetricReporterType = enum_type_wrapper.EnumTypeWrapper(_METRICREPORTERTYPE)
B3 = 0
TRACECONTEXT = 1
UNSPECIFIED = 0
ZIPKIN = 1
OTLP = 2
LOGGING = 3
NONE = 4
OTLP_HTTP = 5
METRIC_REPORTER_TYPE_UNSPECIFIED = 0
METRIC_REPORTER_TYPE_OTLP = 1
METRIC_REPORTER_TYPE_PROMETHEUS = 2
METRIC_REPORTER_TYPE_LOGGING = 3
METRIC_REPORTER_TYPE_NONE = 4



_AGENTCONFIG_RESOURCEATTRIBUTESENTRY = _descriptor.Descriptor(
  name='ResourceAttributesEntry',
  full_name='hypertrace.agent.config.v1.AgentConfig.ResourceAttributesEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='hypertrace.agent.config.v1.AgentConfig.ResourceAttributesEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='hypertrace.agent.config.v1.AgentConfig.ResourceAttributesEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=538,
  serialized_end=595,
)

_AGENTCONFIG = _descriptor.Descriptor(
  name='AgentConfig',
  full_name='hypertrace.agent.config.v1.AgentConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='service_name', full_name='hypertrace.agent.config.v1.AgentConfig.service_name', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='reporting', full_name='hypertrace.agent.config.v1.AgentConfig.reporting', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data_capture', full_name='hypertrace.agent.config.v1.AgentConfig.data_capture', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='propagation_formats', full_name='hypertrace.agent.config.v1.AgentConfig.propagation_formats', index=3,
      number=4, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='enabled', full_name='hypertrace.agent.config.v1.AgentConfig.enabled', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='javaagent', full_name='hypertrace.agent.config.v1.AgentConfig.javaagent', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='resource_attributes', full_name='hypertrace.agent.config.v1.AgentConfig.resource_attributes', index=6,
      number=7, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_AGENTCONFIG_RESOURCEATTRIBUTESENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=77,
  serialized_end=595,
)


_REPORTING = _descriptor.Descriptor(
  name='Reporting',
  full_name='hypertrace.agent.config.v1.Reporting',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='endpoint', full_name='hypertrace.agent.config.v1.Reporting.endpoint', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='secure', full_name='hypertrace.agent.config.v1.Reporting.secure', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='token', full_name='hypertrace.agent.config.v1.Reporting.token', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='trace_reporter_type', full_name='hypertrace.agent.config.v1.Reporting.trace_reporter_type', index=3,
      number=5, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='cert_file', full_name='hypertrace.agent.config.v1.Reporting.cert_file', index=4,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metric_endpoint', full_name='hypertrace.agent.config.v1.Reporting.metric_endpoint', index=5,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metric_reporter_type', full_name='hypertrace.agent.config.v1.Reporting.metric_reporter_type', index=6,
      number=8, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=598,
  serialized_end=1004,
)


_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='hypertrace.agent.config.v1.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='request', full_name='hypertrace.agent.config.v1.Message.request', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='response', full_name='hypertrace.agent.config.v1.Message.response', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1006,
  serialized_end=1106,
)


_DATACAPTURE = _descriptor.Descriptor(
  name='DataCapture',
  full_name='hypertrace.agent.config.v1.DataCapture',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='http_headers', full_name='hypertrace.agent.config.v1.DataCapture.http_headers', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='http_body', full_name='hypertrace.agent.config.v1.DataCapture.http_body', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rpc_metadata', full_name='hypertrace.agent.config.v1.DataCapture.rpc_metadata', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rpc_body', full_name='hypertrace.agent.config.v1.DataCapture.rpc_body', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='body_max_size_bytes', full_name='hypertrace.agent.config.v1.DataCapture.body_max_size_bytes', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='body_max_processing_size_bytes', full_name='hypertrace.agent.config.v1.DataCapture.body_max_processing_size_bytes', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1109,
  serialized_end=1478,
)


_JAVAAGENT = _descriptor.Descriptor(
  name='JavaAgent',
  full_name='hypertrace.agent.config.v1.JavaAgent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='filter_jar_paths', full_name='hypertrace.agent.config.v1.JavaAgent.filter_jar_paths', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1480,
  serialized_end=1547,
)

_AGENTCONFIG_RESOURCEATTRIBUTESENTRY.containing_type = _AGENTCONFIG
_AGENTCONFIG.fields_by_name['service_name'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_AGENTCONFIG.fields_by_name['reporting'].message_type = _REPORTING
_AGENTCONFIG.fields_by_name['data_capture'].message_type = _DATACAPTURE
_AGENTCONFIG.fields_by_name['propagation_formats'].enum_type = _PROPAGATIONFORMAT
_AGENTCONFIG.fields_by_name['enabled'].message_type = google_dot_protobuf_dot_wrappers__pb2._BOOLVALUE
_AGENTCONFIG.fields_by_name['javaagent'].message_type = _JAVAAGENT
_AGENTCONFIG.fields_by_name['resource_attributes'].message_type = _AGENTCONFIG_RESOURCEATTRIBUTESENTRY
_REPORTING.fields_by_name['endpoint'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_REPORTING.fields_by_name['secure'].message_type = google_dot_protobuf_dot_wrappers__pb2._BOOLVALUE
_REPORTING.fields_by_name['token'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_REPORTING.fields_by_name['trace_reporter_type'].enum_type = _TRACEREPORTERTYPE
_REPORTING.fields_by_name['cert_file'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_REPORTING.fields_by_name['metric_endpoint'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_REPORTING.fields_by_name['metric_reporter_type'].enum_type = _METRICREPORTERTYPE
_MESSAGE.fields_by_name['request'].message_type = google_dot_protobuf_dot_wrappers__pb2._BOOLVALUE
_MESSAGE.fields_by_name['response'].message_type = google_dot_protobuf_dot_wrappers__pb2._BOOLVALUE
_DATACAPTURE.fields_by_name['http_headers'].message_type = _MESSAGE
_DATACAPTURE.fields_by_name['http_body'].message_type = _MESSAGE
_DATACAPTURE.fields_by_name['rpc_metadata'].message_type = _MESSAGE
_DATACAPTURE.fields_by_name['rpc_body'].message_type = _MESSAGE
_DATACAPTURE.fields_by_name['body_max_size_bytes'].message_type = google_dot_protobuf_dot_wrappers__pb2._INT32VALUE
_DATACAPTURE.fields_by_name['body_max_processing_size_bytes'].message_type = google_dot_protobuf_dot_wrappers__pb2._INT32VALUE
_JAVAAGENT.fields_by_name['filter_jar_paths'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
DESCRIPTOR.message_types_by_name['AgentConfig'] = _AGENTCONFIG
DESCRIPTOR.message_types_by_name['Reporting'] = _REPORTING
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['DataCapture'] = _DATACAPTURE
DESCRIPTOR.message_types_by_name['JavaAgent'] = _JAVAAGENT
DESCRIPTOR.enum_types_by_name['PropagationFormat'] = _PROPAGATIONFORMAT
DESCRIPTOR.enum_types_by_name['TraceReporterType'] = _TRACEREPORTERTYPE
DESCRIPTOR.enum_types_by_name['MetricReporterType'] = _METRICREPORTERTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AgentConfig = _reflection.GeneratedProtocolMessageType('AgentConfig', (_message.Message,), {

  'ResourceAttributesEntry' : _reflection.GeneratedProtocolMessageType('ResourceAttributesEntry', (_message.Message,), {
    'DESCRIPTOR' : _AGENTCONFIG_RESOURCEATTRIBUTESENTRY,
    '__module__' : 'config_pb2'
    # @@protoc_insertion_point(class_scope:hypertrace.agent.config.v1.AgentConfig.ResourceAttributesEntry)
    })
  ,
  'DESCRIPTOR' : _AGENTCONFIG,
  '__module__' : 'config_pb2'
  # @@protoc_insertion_point(class_scope:hypertrace.agent.config.v1.AgentConfig)
  })
_sym_db.RegisterMessage(AgentConfig)
_sym_db.RegisterMessage(AgentConfig.ResourceAttributesEntry)

Reporting = _reflection.GeneratedProtocolMessageType('Reporting', (_message.Message,), {
  'DESCRIPTOR' : _REPORTING,
  '__module__' : 'config_pb2'
  # @@protoc_insertion_point(class_scope:hypertrace.agent.config.v1.Reporting)
  })
_sym_db.RegisterMessage(Reporting)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), {
  'DESCRIPTOR' : _MESSAGE,
  '__module__' : 'config_pb2'
  # @@protoc_insertion_point(class_scope:hypertrace.agent.config.v1.Message)
  })
_sym_db.RegisterMessage(Message)

DataCapture = _reflection.GeneratedProtocolMessageType('DataCapture', (_message.Message,), {
  'DESCRIPTOR' : _DATACAPTURE,
  '__module__' : 'config_pb2'
  # @@protoc_insertion_point(class_scope:hypertrace.agent.config.v1.DataCapture)
  })
_sym_db.RegisterMessage(DataCapture)

JavaAgent = _reflection.GeneratedProtocolMessageType('JavaAgent', (_message.Message,), {
  'DESCRIPTOR' : _JAVAAGENT,
  '__module__' : 'config_pb2'
  # @@protoc_insertion_point(class_scope:hypertrace.agent.config.v1.JavaAgent)
  })
_sym_db.RegisterMessage(JavaAgent)


DESCRIPTOR._options = None
_AGENTCONFIG_RESOURCEATTRIBUTESENTRY._options = None
# @@protoc_insertion_point(module_scope)
