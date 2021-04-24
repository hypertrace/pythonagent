install-deps:
	pip3 install -r requirements.txt

run-backend:
	@rm -rf __pycache__ || true
	HT_CONFIG_FILE=./config.yaml FLASK_APP="backend:create_app()" FLASK_ENV=development flask run -p 8081

run-hypertrace:
	docker-compose up