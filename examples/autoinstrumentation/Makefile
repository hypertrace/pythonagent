install-deps:
	pip3 install -r requirements.txt

run:
	@rm -rf __pycache__ || true
	HT_CONFIG_FILE=./config.yaml hypertrace-instrument flask run -p 9000

run-hypertrace:
	docker-compose -f docker-compose-hypertrace.yml up --renew-anon-volumes -d

run-mysql:
	docker-compose -f ./mysql/docker-compose.yml up --renew-anon-volumes -d
