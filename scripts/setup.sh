#!/bin/sh

apt update && apt install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa
# apt install python-is-python3
apt update && apt install -y ansible python3.9