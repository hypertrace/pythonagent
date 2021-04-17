#!/bin/bash

DIRS=(flask \
      grpc  \
      mysql \
      postgresql \
      gunicorn \
      requests \
      aiohttp)
BASE_TEST_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for DIR in ${DIRS[@]}
do
  PWD_=`pwd`
  echo "Running tests in ${BASE_TEST_DIR}/../test/${DIR}"
  cd ${BASE_TEST_DIR}/../test/${DIR}
  tox
  rc=$?
  if [ $rc -ne 0 ];
  then
    echo "Test failed"
    exit 0
  fi
  cd ${PWD_}
done
