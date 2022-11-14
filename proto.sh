# /bin/sh
PROTO_VERSION=3.13.0
OS=$1 #osx for local

rm -rf ./protoc
curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v${PROTO_VERSION}/protoc-${PROTO_VERSION}-${OS}-x86_64.zip
unzip protoc-${PROTO_VERSION}-${OS}-x86_64.zip -d ./protoc
./protoc/bin/protoc --python_out=src/hypertrace/agent/config \
		   --proto_path=src/agent-config/proto/hypertrace/agent/config/v1/ \
		    ./src/agent-config/proto/hypertrace/agent/config/v1/config.proto