#!/bin/bash

mkdir -p /tests-"$2"/ansible_collections/avantra
cp -r . /tests-"$2"/ansible_collections/avantra/core
cd /tests-"$2"/ansible_collections/avantra/core
rm -rf scripts
rm -f bitbucket-pipelines.yml

if [ -z "$3" ]
  then
    python -m pip install "ansible-core>=$2"
else
  python -m pip install "ansible-core>=$2,<$3"
fi

ansible-test sanity --junit --python "$1"

return_code=$?
if [ $return_code -ne 0 ]; then
  echo "************ SANITY FAILED************"
  exit $return_code
fi

ansible-test units --coverage --python "$1" --requirements

return_code=$?
if [ $return_code -ne 0 ]; then
  echo "************ UNIT TESTS FAILED************"
  exit $return_code
fi

ansible-test coverage report --requirements

ln -s tests/output test-results