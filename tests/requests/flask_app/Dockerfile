FROM python:3.7.9

WORKDIR usr/src/flask_app
COPY tests/requests/flask_app/requirements.txt .
COPY src/hypertrace/ /usr/src/flask_app/hypertrace/
COPY requirements.txt /usr/src/flask_app/hypertrace/agent_requirements.txt

RUN pip list
RUN ls
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r /usr/src/flask_app/hypertrace/agent_requirements.txt

COPY tests/requests/flask_app/* /usr/src/flask_app/
