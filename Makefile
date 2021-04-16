TEST_DIR=test

hypertrace_test:
	cd ${TEST_DIR}/flask; tox
	cd ${TEST_DIR}/grpc; tox
	cd ${TEST_DIR}/mysql; tox
	cd ${TEST_DIR}/postgresql; tox
	cd ${TEST_DIR}/gunicorn; tox
	cd ${TEST_DIR}/requests; tox
	cd ${TEST_DIR}/aiohttp; tox
