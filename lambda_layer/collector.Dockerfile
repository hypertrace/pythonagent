FROM golang:1.16.5
RUN apt-get update -y && apt-get install unzip zip -y

RUN mkdir /volume-copy
WORKDIR project

RUN git clone https://github.com/open-telemetry/opentelemetry-lambda .
# latest commit 8e77f5b has created an issue with otel-collector extension layer
# causing lambda to not run, using commit prior to that
RUN git checkout b09ea2e6b998

RUN cd collector && make build

RUN mkdir -p ./collector/build/extensions
# Move in config template
RUN mkdir ./collector/build/extensions/config
COPY collector.template.yaml ./collector/build/extensions/config/collector.yaml
# Move original collector exec to different directory, out of extensions dir
RUN mkdir -p ./collector/build/extensions/exec
RUN cp ./collector/build/extensions/collector ./collector/build/extensions/exec

COPY collector ./collector/build/extensions/collector

RUN cd collector/build && zip -r collector-extension.zip extensions
CMD cp -r collector/build/* /volume-copy