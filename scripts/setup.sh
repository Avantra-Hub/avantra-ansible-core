#!/bin/sh

# apt install python-is-python3
add-apt-repository ppa:deadsnakes/ppa
apt update && apt install -y ansible python3.9