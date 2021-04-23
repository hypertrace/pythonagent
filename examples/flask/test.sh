#!/bin/bash
export HT_TRACES_EXPORTER=zipkin
export HT_REPORTING_ENDPOINT=http://localhost:9411/api/v2/spans
docker-compose up -d
sleep 10
python test_basic.py
python test_validate.py
rc=$?
if [ $rc -ne 0 ];
then
  echo "An error occurred running the test."
  exit 1
fi
