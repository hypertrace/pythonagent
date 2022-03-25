#!/bin/bash
PYTHON_PATH=../../src:$PYTHON_PATH
SPAN=`HT_SKIP_MODULES="mysql" HT_ENABLE_CONSOLE_SPAN_EXPORTER=True python ../../../src/hypertrace/agent/autoinstrumentation/hypertrace_instrument.py python test_flask_1.py | egrep -v "INFO|DEBUG"`
echo SPAN=${SPAN}
TRACE_ID=`echo ${SPAN} | jq .context.trace_id | sed 's/\"//g'`
echo TRACE_ID=$TRACE_ID
if [ -z "${TRACE_ID}" ];
then
  echo "Didn't find TRACE_ID."
  exit 1
fi
METHOD=`echo ${SPAN} | jq '.attributes."http.method"' | sed 's/\"//g'`
echo METHOD=${METHOD}
if [ "${METHOD}" != "GET" ];
then
  echo "Didn't find METHOD."
  exit 1
fi
TARGET=`echo ${SPAN} | jq '.attributes."http.target"' | sed 's/\"//g'`
echo TARGET=${TARGET}
if [ "${TARGET}" != "/route1" ];
then
  echo "Didn't find TARGET."
  exit 1
fi
RESPONSE_CONTENT_TYPE=`echo ${SPAN} | jq '.attributes."http.response.header.content-type"' | sed 's/\"//g'`
echo RESPONSE_CONTENT_TYPE=${RESPONSE_CONTENT_TYPE}
if [ "${RESPONSE_CONTENT_TYPE}" != "application/json" ];
then
  echo "Didn't find RESPONSE_CONTENT_TYPE."
  exit 1
fi
CUSTOM_REQUEST_HEADER=`echo ${SPAN} | jq '.attributes."http.request.header.tester1"' | sed 's/\"//g'`
echo CUSTOM_REQUEST_HEADER=${CUSTOM_REQUEST_HEADER}
if [ "${CUSTOM_REQUEST_HEADER}" != "tester1" ];
then
  echo "Didn't find CUSTOM_REQUEST_HEADER."
  exit 1
fi
CUSTOM_RESPONSE_HEADER=`echo ${SPAN} | jq '.attributes."http.response.header.tester3"' | sed 's/\"//g'`
echo CUSTOM_RESPONSE_HEADER=${CUSTOM_RESPONSE_HEADER}
if [ "${CUSTOM_RESPONSE_HEADER}" != "tester3" ];
then
  echo "Didn't find CUSTOM_RESPONSE_HEADER."
  exit 1
fi
RESPONSE_BODY=`echo ${SPAN} | jq '.attributes."http.response.body"' | sed 's/\"//g'`
echo RESPONSE_BODY=${RESPONSE_BODY}
if [ "${RESPONSE_BODY}" != "{ \\"a\\": \\"a\\", \\"xyz\\": \\"xyz\\" }" ];
then
  echo "Didn't find RESPONSE_BODY."
  exit 1
fi
HTTP_STATUS_CODE=`echo ${SPAN} | jq '.attributes."http.status_code"' | sed 's/\"//g'`
echo HTTP_STATUS_CODE=${HTTP_STATUS_CODE}
if [ "${HTTP_STATUS_CODE}" != "200" ];
then
  echo "Didn't find HTTP_STATUS_CODE."
  exit 1
fi
exit 0
