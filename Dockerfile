FROM python:3.8-alpine

RUN apk add --no-cache build-base linux-headers git
RUN pip install git+https://github.com/hypertrace/pythonagent.git@main
#RUN pip install -Iv opentelemetry-exporter-otlp==1.1.0
#RUN pip install -Iv opentelemetry-exporter-otlp-proto-grpc==1.1.0