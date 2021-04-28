TEST_DIR=tests

.PHONY: test-unit
test-unit:
	tox -e test-unit

.PHONY: test-integration
test-integration: # Call through tests_py37 | tests_py38 | tests_py39
	@echo "Running tests over ${PY_TARGET}" 
	cd ${TEST_DIR}/flask; tox -e ${PY_TARGET}
	cd ${TEST_DIR}/grpc; tox -e ${PY_TARGET}
	cd ${TEST_DIR}/mysql; tox -e ${PY_TARGET}
	cd ${TEST_DIR}/postgresql; tox -e ${PY_TARGET}
	cd ${TEST_DIR}/gunicorn; tox -e ${PY_TARGET}
	cd ${TEST_DIR}/requests; tox -e ${PY_TARGET}
	cd ${TEST_DIR}/aiohttp; tox -e ${PY_TARGET}
	cd ${TEST_DIR}/docker; tox -e ${PY_TARGET}

.PHONY: test
test: test-unit test-integration

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

build_protobuf:
	protoc --python_out=src/hypertrace/agent/config \
          -I src/protobuf-config/agent-config/tools/env-vars-generator/protobuf/src \
          -Isrc/protobuf-config/agent-config \
          src/protobuf-config/agent-config/config.proto
