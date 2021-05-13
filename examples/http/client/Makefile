install-deps:
	pip3 install -r requirements.txt

run:
	@rm -rf __pycache__ || true
	STREAM=${STREAM} HT_CONFIG_FILE=./config.yaml python client.py

run-hypertrace:
	docker-compose -f docker-compose-hypertrace.yml up --renew-anon-volumes -d
