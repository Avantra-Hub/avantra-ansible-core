#!/bin/sh

apt update && apt install -y ansible
echo "$PATH"
ansible-test sanity