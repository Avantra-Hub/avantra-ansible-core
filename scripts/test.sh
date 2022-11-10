#!/bin/sh

pwd
ls -la
cp -r . core
mkdir -p ansible_collections/avantra
mv core ansible_collections/avantra
cd ansible_collections/avantra/core
pwd
ls -la
/usr/bin/ansible-test sanity