#!/bin/bash

mkdir -p /tests-devel/ansible_collections/avantra
cp -r . /tests-devel/ansible_collections/avantra/core

cd /root
# From https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-for-development
git clone https://github.com/ansible/ansible.git
cd /root/ansible
source ./hacking/env-setup
python3 -m pip install --user -r ./requirements.txt



cd /tests-devel/ansible_collections/avantra/core
rm -rf scripts
rm -f bitbucket-pipelines.yml

ansible-test sanity --junit --python "$1"

return_code=$?
if [ $return_code -ne 0 ]; then
  echo "************ SANITY FAILED************"
  exit $return_code
fi

ansible-test units --coverage --python "$1" --requirements

return_code=$?
if [ $return_code -ne 0 ]; then
  echo "************ UNIT TESTS FAILED************"
  exit $return_code
fi

ansible-test coverage report --requirements

ln -s tests/output test-results