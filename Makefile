TEST_DIR=test

test_py3.7: PY_VERSION=py37
test_py3.7: test

test_py3.8: PY_VERSION=py38
test_py3.8: test

test_py3.9: PY_VERSION=py39
test_py3.9: test

.PHONY: test
test: # Call through test_py37 | test_py38 | test_py39
	cd ${TEST_DIR}/flask; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/grpc; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/mysql; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/postgresql; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/gunicorn; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/requests; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/aiohttp; tox -e ${PY_VERSION}
	cd ${TEST_DIR}/docker; tox -e ${PY_VERSION}

.PHONY: build
build: build_protobuf
	python3 -m pip install --upgrade build
	python -m build

.PHONY: clean
clean:
	rm -Rf build dist src/hypertrace.egg-info

.PHONY: docs
docs:
	tox -e pdoc

.PHONY: lint
lint:
	tox -e lint

.PHONY: install
install: build
	pip uninstall hypertrace -y
	pip install dist/hypertrace-0.1.0.tar.gz

unittest:
	tox -e unittest

build_protobuf:
	protoc --python_out=src/hypertrace/agent/config \
          -I src/protobuf-config/agent-config/tools/env-vars-generator/protobuf/src \
          -Isrc/protobuf-config/agent-config \
          src/protobuf-config/agent-config/config.proto
