FROM python:3.7.9

WORKDIR usr/src/flask_app
COPY tests/gunicorn/flask_app/requirements.txt .
COPY src/hypertrace/ /usr/src/flask_app/hypertrace/
RUN ls
RUN pip install --no-cache-dir -r requirements.txt
COPY tests/gunicorn/flask_app/* /usr/src/flask_app/
