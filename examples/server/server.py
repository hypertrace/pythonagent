from flask import Flask, request, jsonify, make_response, Response
from hypertrace.agent import Agent
import time
import json
import logging
import mysql.connector


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def stream_body(res_body: str):
    new_line_chars = ['{', '}', ',', '[', ']']
    for c in res_body:
        time.sleep(0.3)
        logging.debug("Sending response chunk")
        if c in new_line_chars:
            yield c + "\n"
        else:
            yield c


def insert_user(name: str) -> int:
    cnx = mysql.connector.connect(database='test',
                                  username='root',
                                  password='root',
                                  host='localhost',
                                  port=3306)
    cursor = cnx.cursor()
    query = "INSERT INTO users (`name`) VALUES (%s)"
    cursor.execute(query, (name,))
    id = cursor.lastrowid
    cnx.close()
    return id


def create_app():
    app = Flask(__name__)
    agent = Agent()
    agent.register_flask_app(app)
    agent.register_mysql()

    @app.route('/', methods=['POST'])
    def hello():
        request_data = request.get_json()
        name = request_data['name']

        user_id = insert_user(name)

        res_body = {'id': user_id, 'message': f'Hello {name}'}

        stream = request.args.get('stream')
        if stream == 'true':
            # Send the response as stream
            return Response(stream_body(json.dumps(res_body)), mimetype='application/json')
        else:
            # Send the entire response
            response = make_response(jsonify(res_body))
            response.headers['Content-Type'] = 'application/json'
            return response
    return app
