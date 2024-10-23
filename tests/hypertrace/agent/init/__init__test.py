"""Agent init test"""

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPGrpcSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHttpSpanExporter
# from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter
from hypertrace.agent.config import config_pb2


def test_otlp_http_exporter_can_init(agent):
    exporter = agent._init._init_exporter(config_pb2.TraceReporterType.OTLP_HTTP)
    exporter.shutdown()
    assert isinstance(exporter, OTLPHttpSpanExporter)

def test_otlp_grpc_exporter_can_init(agent):
    exporter = agent._init._init_exporter(config_pb2.TraceReporterType.OTLP)
    exporter.shutdown()
    assert isinstance(exporter, OTLPGrpcSpanExporter)

def test_zipkin_exporter_can_init(agent):
    # Disable until otel zipkin is updated for newer protobuf
    pass
    #exporter = agent._init._init_exporter(config_pb2.TraceReporterType.ZIPKIN)
    #exporter.shutdown()
    # assert isinstance(exporter, ZipkinExporter)

