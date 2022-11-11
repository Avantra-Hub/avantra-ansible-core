#!/bin/bash



current_dir=$(pwd)


version=$(python << EOF
    import yaml
    with open('galaxy.yml','r') as galaxy_yml:
      print(yaml.safe_load(galaxy_yml).get("version"))
EOF
)

mkdir -p /build-"$1"/ansible_collections/avantra
cp -r . /build-"$1"/ansible_collections/avantra/core
cd /build-"$1"/ansible_collections/avantra/core

python -m pip install "ansible-core>=$1"

mkdir -p "$current_dir"/build
ansible-galaxy collection build --output-path "$current_dir"/build

python -m venv .venv
source .venv/bin/activate


echo "**************************************** $version"

ls -la

