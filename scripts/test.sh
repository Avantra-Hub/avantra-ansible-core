#!/bin/sh

pwd
ls -la
mkdir -p ./ansible_collections/avantra
cd ./ansible_collections/avantra
ln -s ../.. core
cd core
pwd
ls -la
/usr/bin/ansible-test sanity