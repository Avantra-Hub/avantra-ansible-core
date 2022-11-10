#!/bin/sh

mkdir -p /ansible_collections/avantra
ln -s /ansible_collections/avantra/core .
/usr/bin/ansible-test sanity