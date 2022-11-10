#!/bin/sh

apt update
apt upgrade -y
apt install -y ansible
echo "$PATH"
ansible-test sanity