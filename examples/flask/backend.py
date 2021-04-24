from flask import Flask
from hypertrace.agent import Agent


def create_app():
    app = Flask(__name__)
    agent = Agent()
    agent.register_flask_app(app)

    @app.route('/')
    def hello():
        return '{"message": "Hello World"}'
    return app
