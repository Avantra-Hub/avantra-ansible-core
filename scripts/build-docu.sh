#!/bin/bash

current_dir=$(pwd)

python3 -m pip install pyyaml
version=$(python << EOF
import yaml
with open('galaxy.yml','r') as galaxy_yml:
    print(yaml.safe_load(galaxy_yml).get("version"))
EOF
)

apt-get update && apt-get install rsync -y

python -m pip install "ansible-core>=$1"

ls -la
ansible-galaxy collection install build/avantra-core-"$version".tar.gz

mkdir -p /root/ansible-docu
cd /root/ansible-docu || { echo "cd /root/ansible-docu impossible"; exit 1; }

git clone https://github.com/ansible-community/antsibull-core.git
git clone https://github.com/ansible-community/antsibull-docs.git
cd antsibull-docs || { echo "cd antsibull-docs impossible"; exit 1; }
python3 -m pip install poetry==1.2.2
poetry install
mkdir dest
chmod 644 dest
poetry run antsibull-docs sphinx-init --use-current --dest-dir dest avantra.core
chmod -R 644 dest
cd dest || { echo "cd dest impossible"; exit 1; }
dest_dir=$(pwd)
#python3 -m pip install -r requirements.txt
set -e
cd "$dest_dir" || { echo "cd $dest_dir impossible"; exit 1; }

mkdir temp-rst
chmod -R 744 .
antsibull-docs \
    --config-file antsibull-docs.cfg \
    collection \
    --use-current \
    --dest-dir temp-rst \
    avantra.core

# Copy collection documentation into source directory
rsync -cprv --delete-after temp-rst/collections/ rst/collections/

# Build Sphinx site
sphinx-build -M html rst build -c . -W --keep-going
cp -r build/* "$current_dir"/build