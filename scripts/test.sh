#!/bin/sh

cp -r . core
mkdir -p ansible_collections/avantra
mv core ansible_collections/avantra
cd ansible_collections/avantra/core
/usr/bin/ansible-test sanity --docker -vvv