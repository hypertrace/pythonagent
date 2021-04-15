FROM python:3.7.9

WORKDIR usr/src/flask_app
COPY test/gunicorn/flask_app/requirements.txt .
COPY hypertrace/ /usr/src/flask_app/hypertrace/
RUN ls
RUN pip install --no-cache-dir -r requirements.txt
COPY test/gunicorn/flask_app/* /usr/src/flask_app/
