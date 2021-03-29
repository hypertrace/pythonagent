FROM python:3.7.9

WORKDIR usr/src/flask_app
COPY test/gunicorn/flask_app/requirements.txt .
COPY agent/ /usr/src/flask_app/agent/
COPY config/ /usr/src/flask_app/config/
COPY instrumentation/ /usr/src/flask_app/instrumentation/
RUN ls
RUN pip install --no-cache-dir -r requirements.txt
COPY test/gunicorn/flask_app/* /usr/src/flask_app/
