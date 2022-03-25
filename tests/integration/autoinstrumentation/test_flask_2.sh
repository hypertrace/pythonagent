#!/bin/bash
PYTHON_PATH=../../src:$PYTHON_PATH
SPAN=`HT_SKIP_MODULES="flask" HT_ENABLE_CONSOLE_SPAN_EXPORTER=True python ../../../src/hypertrace/agent/autoinstrumentation/hypertrace_instrument.py python test_flask_2.py | egrep -v "INFO|DEBUG"`
echo SPAN=${SPAN}
TRACE_ID=`echo ${SPAN} | jq .context.trace_id | sed 's/\"//g'`
echo TRACE_ID=$TRACE_ID
if [ -z "${TRACE_ID}" ];
then
  echo "Didn't find TRACE_ID."
  exit 1
fi
SQL_STATEMENT=`echo ${SPAN} | jq '.attributes."db.statement"' | sed 's/\"//g'`
echo SQL_STATEMENT=${SQL_STATEMENT}
if [ "${SQL_STATEMENT}" != "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')" ];
then
  echo "Didn't find HTTP_STATUS_CODE."
  exit 1
fi
DB_USER=`echo ${SPAN} | jq '.attributes."db.user"' | sed 's/\"//g'`
echo DB_USER=${DB_USER}
if [ "${DB_USER}" != "root" ];
then
  echo "Didn't find DB_USER."
  exit 1
fi
STATUS_CODE=`echo ${SPAN} | jq '.status."status_code"' | sed 's/\"//g'`
echo STATUS_CODE=${STATUS_CODE}
if [ "${STATUS_CODE}" != "UNSET" ];
then
  echo "Didn't find STATUS_CODE."
  exit 1
fi

exit 0
