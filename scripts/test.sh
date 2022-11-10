#!/bin/sh

mkdir -p /tests-"$2"/ansible_collections/avantra
cp -r . /tests-"$2"/ansible_collections/avantra/core
cd /tests-"$2"/ansible_collections/avantra/core

if [ -z "$3" ]
  then
    python -m pip install "ansible-core>=$2"
else
  python -m pip install "ansible-core>=$2,<$3"
fi

ansible-test sanity --junit --python "$1"

//It contains the status of the last executed command
if [[ $? -eq 0 ]]; then
  echo "success*********"
  exit 0
else
  echo "failed************"
  exit 1
fi

ansible-test units --coverage --python "$1" --requirements
ansible-test coverage xml --requirements

ln -s tests/output test-results