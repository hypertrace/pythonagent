#!/bin/bash

TEST_DIR=tests

PYTHON_VERSION ?= $(shell python --version | cut -c8- | cut -d'.' -f 1-2) # e.g. 3.9
PY_TARGET=py$(subst .,,$(PYTHON_VERSION)) # e.g. py39
LOG_LEVEL ?= INFO

.PHONY: unit-test
unit-test:
	cd tests/externalServices && docker-compose up -d && cd ../../
	python3 setup.py develop
	python3 -m pytest tests/hypertrace
	cd tests/externalServices && docker-compose down

.PHONY: integration-test
integration-test:
	cd ${TEST_DIR}/integration/autoinstrumentation; HT_LOG_LEVEL=${LOG_LEVEL} tox -e ${PY_TARGET}
	cd ${TEST_DIR}/integration/gunicorn; HT_LOG_LEVEL=${LOG_LEVEL} tox -e ${PY_TARGET}

.PHONY: test
test: unit-test integration-test

.PHONY: build-proto
build-proto:
	git submodules update --init --recursive
	protoc --python_out=src/hypertrace/agent/config \
		   --proto_path=src/agent-config/proto/hypertrace/agent/config/v1/ \
		    ./src/agent-config/proto/hypertrace/agent/config/v1/config.proto

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
