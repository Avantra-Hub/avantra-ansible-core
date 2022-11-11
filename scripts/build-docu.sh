#!/bin/bash

mkdir -p /root/ansible-docu
cd /root/ansible-docu

git clone https://github.com/ansible-community/antsibull-core.git
git clone https://github.com/ansible-community/antsibull-docs.git
cd antsibull-docs
python3 -m pip install poetry
poetry install

mkdir dest
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./build.sh

ls -la dest