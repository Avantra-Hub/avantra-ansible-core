#!/bin/bash

mkdir -p /tests-"$1"/ansible_collections/avantra
cp -r . /tests-"$1"/ansible_collections/avantra/core
cd /tests-"$1"/ansible_collections/avantra/core
python -m venv .venv
echo "Hello1!"
source .venv/bin/activate
echo "Hello!"
deactivate

