TEST_DIR=test

test_py37: PY_VERSION=py37
test_py37: hypertrace_test

test_py38: PY_VERSION=py38
test_py38: hypertrace_test

test_py39: PY_VERSION=py39
test_py39: hypertrace_test

hypertrace_test:
	cd ${TEST_DIR}/flask; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/grpc; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/mysql; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/postgresql; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/gunicorn; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/requests; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/aiohttp; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/docker; tox -e ${PY_VERSION}

build: build_protobuf
	python3 -m pip install --upgrade build
	python -m build
clean:
	rm -Rf build dist src/hypertrace.egg-info

.PHONY: docs
docs: ## Generates the docs
	tox -e pdoc

lint:
	tox -e lint
install: build
	pip install dist/hypertrace-0.1.0.tar.gz

build_protobuf:
	protoc --python_out=src/hypertrace/agent/config \
          -I src/protobuf-config/agent-config/tools/env-vars-generator/protobuf/src \
          -Isrc/protobuf-config/agent-config \
          src/protobuf-config/agent-config/config.proto
