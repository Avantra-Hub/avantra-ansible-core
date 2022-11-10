#!/bin/bash

mkdir -p /tests-"$1"/ansible_collections/avantra
cp -r . /tests-"$1"/ansible_collections/avantra/core
cd /tests-"$1"/ansible_collections/avantra/core
python -m pip install ansible "ansible-core>=$1,<$2"
ansible --version

