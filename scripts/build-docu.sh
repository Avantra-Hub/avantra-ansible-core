#!/bin/bash

current_dir=$(pwd)

python3 -m pip install pyyaml
version=$(python << EOF
import yaml
with open('galaxy.yml','r') as galaxy_yml:
    print(yaml.safe_load(galaxy_yml).get("version"))
EOF
)

python -m pip install "ansible-core>=$1"

ansible-galaxy collection install build/avantra-core-"$version".tar.gz

mkdir -p /root/ansible-docu
cd /root/ansible-docu || { echo "cd /root/ansible-docu impossible"; exit 1; }

git clone https://github.com/ansible-community/antsibull-core.git
git clone https://github.com/ansible-community/antsibull-docs.git
cd antsibull-docs || { echo "cd antsibull-docs impossible"; exit 1; }
python3 -m pip install poetry
poetry install

echo "1: --------------------------------------------------------------------------------"
mkdir dest
echo "2: --------------------------------------------------------------------------------"
chmod 644 dest
echo "3: --------------------------------------------------------------------------------"
poetry run antsibull-docs sphinx-init --use-current --dest-dir dest avantra.core
echo "4: --------------------------------------------------------------------------------"
chmod -R 644 dest
echo "5: --------------------------------------------------------------------------------"
cd dest || { echo "cd dest impossible"; exit 1; }
echo "6: --------------------------------------------------------------------------------"
#python3 -m venv .venv
echo "7: --------------------------------------------------------------------------------"
#source .venv/bin/activate
echo "8: --------------------------------------------------------------------------------"
python3 -m pip install -r requirements.txt
echo "9: --------------------------------------------------------------------------------"
chmod -R 744 .
echo "10: --------------------------------------------------------------------------------"
./build.sh
echo "11: --------------------------------------------------------------------------------"
cp -r build/* "$current_dir"/build