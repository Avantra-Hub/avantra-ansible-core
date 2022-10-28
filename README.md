# Ansible Collection - avantra.core

Documentation for the collection.

## Installing this collection ##

**NOTE:** The passwords should be stored in a secure location or
an [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

```properties
[splunk]
avantra-api.host.net
[splunk:vars]
ansible_network_os=splunk.es.splunk
ansible_user=admin
ansible_httpapi_pass=my_super_secret_admin_password
ansible_httpapi_port=8089
ansible_httpapi_use_ssl=yes
ansible_httpapi_validate_certs=True
ansible_connection=httpapi
```

## Using this collection ##

## Uninstalling this collection ##

As there is at the moment no built-in ansible-galaxy command to uninstall a collection remove it from the file system.
Per default this will do the job:

```shell
$ rm -rf ~/.ansible/collections/ansible_collections/avantra/core
```

## Defining the Avantra API variables ##

```shell
ansible-playbook release.yml --extra-vars "avantra_api_user=user avantra_api_password=foo avantra_api_url=https://localhost:8090/xn"
```

## Development ##

### Setup .venv for Python Development ###

```shell
# In the collection directory:
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install ansible-core
# Install the collection to your machine (upgrade it if possible)
$ ansible-galaxy collection install /path/to/collection --upgrade
```

ansible.cfg

```properties
[defaults]
inventory = ./inventory
COLLECTIONS_PATHS=./collections
```

Test whether you can find the avantra.core collection.

```shell
$ ansible-galaxy collection list
```

### Cycle ###

1. Develop
2. Install
   ```shell
   ansible-galaxy collection install . --upgrade
   ```
3. Run
   ```shell
   ansible localhost -m avantra.core.customer -vv --extra-vars "avantra_api_user=user avantra_api_password=foo avantra_api_urk=https://localhost:8090/xn"
   ```

### HTTP Requests ###

To not have to import another python dependency ansible offers an own 'requests' like module to
use to execute HTTP requests: https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/urls.py

### Testing ###

#### Unit Test ###

- tests/units ...
- uses pytest
- ansible-test units --requirements
- ansible-test units --requirements --python 3.10

## Documentation ##

NOTE: The documentation can only be built using python < 3.10. There is a problem in the
sphinx library.

https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_documenting.html#build-collection-docsit

Go to a special directory to build the documentation locally.

```shell
git clone https://github.com/ansible-community/antsibull-core.git
git clone https://github.com/ansible-community/antsibull-docs.git
cd antsibull-docs

python3 -m pip install poetry
poetry install  # Installs dependencies into a virtualenv

mkdir dest
antsibull-docs sphinx-init --use-current --dest-dir dest avantra.core
cd dest
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./build.sh
```

Then open build/html/index.html in a browser of your choice.

---
**NOTES**

- Keep in mind that the documentation strings have to be valid YAML documents.
- In a documentation fragment there has to be at least an options key even if is empty: 
  ```shell
  options: {}    
  ```
---

### References ###

- https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_documenting.html#module-docs-fragments