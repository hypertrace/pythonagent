install-deps:
	pip3 install -r requirements.txt

run:
	@rm -rf __pycache__ || true
	HT_INSTRUMENTED_MODULES=flask HT_ENABLE_CONSOLE_SPAN_EXPORTER=True HT_CONFIG_FILE=./config.yaml FLASK_APP="server:create_app()" FLASK_ENV=development hypertrace-instrument flask run -p 9000

run-hypertrace:
	docker-compose -f docker-compose-hypertrace.yml up --renew-anon-volumes -d

run-mysql:
	docker-compose -f ./mysql/docker-compose.yml up --renew-anon-volumes -d
