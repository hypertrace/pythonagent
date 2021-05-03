#!/bin/bash

TEST_DIR=tests

PYTHON_VERSION ?= $(shell python --version | cut -c8- | cut -d'.' -f 1-2) # e.g. 3.9
PY_TARGET=py$(subst .,,$(PYTHON_VERSION)) # e.g. py39

.PHONY: test-unit
test-unit:
	tox -e test-unit

.PHONY: test-integration
test-integration:
	@echo "Running tests over $(PY_TARGET)" 
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

.PHONY: build-proto
build-proto:
	git submodule update  --init  --recursive
	protoc --python_out=src/hypertrace/agent/config \
          -Isrc/agent-config \
          -Isrc/agent-config/tools/env-vars-generator/protobuf/src \
          src/agent-config/config.proto

.PHONY: build
build: build-proto
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
	pip install dist/hypertrace-*.tar.gz

release:
	@if [[ ! -z "$(git tag -l ${VERSION})" ]]; then echo "Version \"${VERSION}\" already exists."; exit 1 ; fi
	@if [[ -z "${VERSION}" ]]; then echo "VERSION env var is required."; exit 1 ; fi
	$(MAKE) lint test build
	./release.sh ${VERSION}
