FROM python:3.7.9

WORKDIR usr/src/flask_app
COPY tests/docker/requirements.txt .
COPY src/hypertrace/ /usr/src/flask_app/hypertrace/
RUN ls
RUN pip install --no-cache-dir -r requirements.txt
COPY tests/docker/test_flask_1.py /usr/src/flask_app/
RUN pytest -rPx test_flask_1.py
