from flask import Flask, request, jsonify, make_response, Response
from hypertrace.agent import Agent
import time
import json
import logging


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def stream_body(resBody):
    newLineChars = ['{', '}', ',', '[', ']']
    for c in resBody:
        time.sleep(0.3)
        logging.debug("Sending response chunk")
        if c in newLineChars:
            yield c + "\n"
        else:
            yield c


def create_app():
    app = Flask(__name__)
    agent = Agent()
    agent.register_flask_app(app)

    @app.route('/', methods=['POST'])
    def hello():
        request_data = request.get_json()
        name = request_data['name']
        resBody = {'id': 1, 'message': f'Hello {name}'}

        stream = request.args.get('stream')
        if stream == 'true':
            # Send the response as stream
            return Response(stream_body(json.dumps(resBody)), mimetype='application/json')
        else:
            # Send the entire response
            response = make_response(jsonify(resBody))
            response.headers['Content-Type'] = 'application/json'
            return response
    return app
