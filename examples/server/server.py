from flask import Flask, request, jsonify, make_response, Response
from hypertrace.agent import Agent
import time
import json


def stream_body(resBody):
    for c in resBody:
        time.sleep(0.1)
        yield c


def create_app():
    app = Flask(__name__)
    agent = Agent()
    agent.register_flask_app(app)

    @app.route('/', methods=['POST'])
    def hello():
        request_data = request.get_json()
        name = request_data['name']
        resBody = {'message': f'Hello {name}'}

        stream = request.args.get('stream')
        if stream == 'true':
            return Response(stream_body(json.dumps(resBody)), mimetype='application/json')
        else:
            response = make_response(jsonify(resBody))
            response.headers['Content-Type'] = 'application/json'
            return response
    return app
