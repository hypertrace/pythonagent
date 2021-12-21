ARG runtime=python3.9

FROM public.ecr.aws/sam/build-${runtime}

ADD . /workspace

WORKDIR /workspace

RUN mkdir -p /build && \
  python3 -m pip install ./hypertrace-agent-*.tar.gz -t /build/python && \
  mv hypertrace_sdk/hypertrace_wrapper.py /build/python && \
  mv hypertrace_sdk/hypertrace-instrument /build && \
  chmod 755 /build/hypertrace-instrument && \
  rm -rf /build/python/boto* && \
  rm -rf /build/python/urllib3* && \
  cd /build && \
  zip -r layer.zip hypertrace-instrument python

CMD cp /build/layer.zip /out/layer.zip
