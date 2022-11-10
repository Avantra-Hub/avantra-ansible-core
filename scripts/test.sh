#!/bin/sh

mkdir -p ./ansible_collections/avantra
ln -s . ./ansible_collections/avantra/core
cd ./ansible_collections/avantra/core || exit
/usr/bin/ansible-test sanity