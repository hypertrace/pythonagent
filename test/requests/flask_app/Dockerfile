FROM python:3.7.9

WORKDIR usr/src/flask_app
COPY test/requests/flask_app/requirements.txt .
COPY agent/ /usr/src/flask_app/agent/
RUN ls
RUN pip install --no-cache-dir -r requirements.txt
COPY test/requests/flask_app/* /usr/src/flask_app/
