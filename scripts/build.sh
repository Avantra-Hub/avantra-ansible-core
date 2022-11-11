#!/bin/bash

current_dir=$(pwd)

mkdir -p /build-"$1"/ansible_collections/avantra
cp -r . /build-"$1"/ansible_collections/avantra/core
cd /build-"$1"/ansible_collections/avantra/core

python -m pip install "ansible-core>=$1"

ansible-galaxy collection build --output-path "$current_dir"

python -m pip install yq jq
version=$(python -m yq -r .version galaxy.yml)
echo "**************************************** $version"

ls -la

