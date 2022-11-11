#!/bin/bash

mkdir -p /build-"$1"/ansible_collections/avantra
cp -r . /build-"$1"/ansible_collections/avantra/core
cd /build-"$1"/ansible_collections/avantra/core

python -m pip install "ansible-core>=$1" yq

ansible-galaxy collection build

version=$(yq -r .version galaxy.yml)
echo "**************************************** $version"

ls -la

