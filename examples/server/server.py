from flask import Flask, request, jsonify, make_response
from hypertrace.agent import Agent

def create_app():
    app = Flask(__name__)
    agent = Agent()
    agent.register_flask_app(app)

    @app.route('/', methods=['POST'])
    def hello():
        request_data = request.get_json()
        name = request_data['name']
        response = make_response(jsonify(message=f'Hello {name}'))
        response.headers["Content-Type"] = "application/json"
        return response
    return app
