# File: AgentInit.py
# Author: Nitin Sahai
# Date: 03/04/2021
# Notes
#
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)

class AgentInit:
  def __init__(self):
    print('Initializing AgentInit object.')
  def dumpConfig():
    print('Calling DumpConfig().')
    print('RCBJ0001') 

  def flaskInit(self, app):
    print('Calling flaskInit().')
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
      SimpleExportSpanProcessor(ConsoleSpanExporter())
    )
    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
