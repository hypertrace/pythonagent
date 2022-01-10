FROM golang:1.16.5
RUN apt-get update -y && apt-get install unzip zip -y

RUN mkdir /volume-copy
WORKDIR project

RUN git clone https://github.com/open-telemetry/opentelemetry-lambda .
# latest commit 8e77f5b has created an issue with otel-collector extension layer
# causing lambda to not run, using commit prior to that
RUN git checkout b09ea2e6b998

RUN cd collector && make package
RUN ls collector/build

CMD cp -r collector/build/* /volume-copy