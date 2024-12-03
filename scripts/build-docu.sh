#!/bin/bash

current_dir=$(pwd)

echo
echo "---- [READING VERSION] ------------------------------------------------------------------------------------------------"

python3 -m pip install pyyaml
version=$(python << EOF
import yaml
with open('galaxy.yml','r') as galaxy_yml:
    print(yaml.safe_load(galaxy_yml).get("version"))
EOF
)

echo
echo "---- [INSTALL RSYNC] --------------------------------------------------------------------------------------------------"
apt-get update && apt-get install rsync -y
python3 -m pip install "ansible-core>=$1"

echo
echo "---- [INSTALL 'avantra-core-$version] ---------------------------------------------------------------------------------"
ansible-galaxy collection install build/avantra-core-"$version".tar.gz

mkdir -p  $current_dir/target/ansible-docu
cd $current_dir//target/ansible-docu || { echo "cd $current_dir//target/ansible-docu impossible"; exit 1; }

echo
echo "---- [CREATE VIRTUALENV] ----------------------------------------------------------------------------------------------"
python3 -m venv .antsibull-docs-venv
. .antsibull-docs-venv/bin/activate

echo
echo "---- [INSTALL ansible-core and antsibull-docs] ------------------------------------------------------------------------"
python -m pip install ansible-core antsibull-docs sphinx_ansible_theme

echo
echo "---- [CREATE 'dest' directory] ----------------------------------------------------------------------------------------"
mkdir -m 700 "dest"

echo
echo "---- [INIT sphinx directory -> dest] ----------------------------------------------------------------------------------"
antsibull-docs sphinx-init --use-current --dest-dir dest avantra.core
cd dest || { echo "cd dest impossible"; exit 1; }
dest_dir=$(pwd)
#python -m pip install -r requirements.txt

echo
echo "---- [BUILD DOCU] -----------------------------------------------------------------------------------------------------"
mkdir temp-rst
chmod -R 700 temp-rst
antsibull-docs \
    collection \
    --use-current \
    --dest-dir temp-rst \
    avantra.core

# Copy collection documentation into source directory
echo
echo "---- [RSYNC to rst/collections] ---------------------------------------------------------------------------------------"
# Check if the directory exists
if [ ! -d "rst" ]; then
  # Create the directory with permission 700
  mkdir -m 700 "rst"
  echo "Directory 'rst' created with permission 700."
else
  echo "Directory 'rst' already exists."
fi

rsync -cprv --delete-after temp-rst/collections/ rst/collections/


# Build Sphinx site
echo
echo "---- [SPHINX BUILD] ---------------------------------------------------------------------------------------------------"
sphinx-build -M html rst build -c . -W --keep-going

echo
echo "---- [COPY BUILD RESULT] ----------------------------------------------------------------------------------------------"
cp -r build/* "$current_dir"/build