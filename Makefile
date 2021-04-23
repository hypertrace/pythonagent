TEST_DIR=test

.PHONY: test
test:
	cd ${TEST_DIR}/flask; tox
	cd ${TEST_DIR}/grpc; tox
	cd ${TEST_DIR}/mysql; tox
	cd ${TEST_DIR}/postgresql; tox
	cd ${TEST_DIR}/gunicorn; tox
	cd ${TEST_DIR}/requests; tox
	cd ${TEST_DIR}/aiohttp; tox
	cd ${TEST_DIR}/docker; tox

.PHONY: build
build:
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
install:
	pip install dist/hypertrace-0.1.0.tar.gz
