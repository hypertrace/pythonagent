#!/bin/bash

DIRS=(flask \
      grpc \
      mysql \
      postgresql)
BASE_TEST_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for DIR in ${DIRS[@]}
do
  PWD_=`pwd`
  echo "Running tests in ${BASE_TEST_DIR}/../test/${DIR}"
  cd ${BASE_TEST_DIR}/../test/${DIR}
  tox
  cd ${PWD_}
done

