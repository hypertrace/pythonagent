TEST_DIR=test

hypertrace_test:
	cd ${TEST_DIR}/flask; tox
	cd ${TEST_DIR}/grpc; tox
	cd ${TEST_DIR}/mysql; tox
	cd ${TEST_DIR}/postgresql; tox
	cd ${TEST_DIR}/gunicorn; tox
	cd ${TEST_DIR}/requests; tox
	cd ${TEST_DIR}/aiohttp; tox
build:
	python3 -m pip install --upgrade build
	python -m build
clean:
	rm -Rf build dist
docs:
	tox -e pdoc
lint:
	tox -e lint
