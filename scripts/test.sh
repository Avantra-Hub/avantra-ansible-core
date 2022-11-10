#!/bin/sh

mkdir -p /tests-"$1"/ansible_collections/avantra
cp -r . /tests-"$1"/ansible_collections/avantra/core
cd /tests-"$1"/ansible_collections/avantra/core

if [ -z "$2" ]
  then
    python -m pip install ansible "ansible-core>=$1"
else
  python -m pip install ansible "ansible-core>=$1,<$2"
fi

ansible-test coverage erase
ansible-test sanity --junit
ansible-test units --coverage
ansible-test coverage xml
