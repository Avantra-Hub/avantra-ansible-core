#!/bin/bash

mkdir -p /tests-"$1"/ansible_collections/avantra
cp -r . /tests-"$1"/ansible_collections/avantra/core
cd /tests-"$1"/ansible_collections/avantra/core
python -m venv .venv
source .venv/bin/activate

pip install ansible "package>=$1,<$2"

ansible --version

deactivate

