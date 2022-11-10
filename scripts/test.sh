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

ansible-test sanity --junit --python "$1" --requirements
ansible-test units --coverage --python "$1" --requirements
ansible-test coverage xml --requirements
