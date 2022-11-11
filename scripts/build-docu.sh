#!/bin/bash


version=$(python << EOF
import yaml
with open('galaxy.yml','r') as galaxy_yml:
    print(yaml.safe_load(galaxy_yml).get("version"))
EOF
)

ansible-galaxy collection install build/avantra-core-"$version".tar.gz

mkdir -p /root/ansible-docu
cd /root/ansible-docu

git clone https://github.com/ansible-community/antsibull-core.git
git clone https://github.com/ansible-community/antsibull-docs.git
cd antsibull-docs
python3 -m pip install poetry
poetry install

mkdir dest
antsibull-docs sphinx-init --use-current --dest-dir dest avantra.core
cd dest
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./build.sh

ls -la dest