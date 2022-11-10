#!/bin/sh

pwd
ls -la
mkdir -p ./ansible_collections/avantra
ln -s . ./ansible_collections/avantra/core
cd ./ansible_collections/avantra/core/ || exit
pwd
ls -la
/usr/bin/ansible-test sanity