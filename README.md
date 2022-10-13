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
COLLECTIONS_PATHS = ./collections
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
   ansible localhost -m avantra.core.customer -vv --extra-vars "avantra_api_user=user avantra_api_password=foo avantra_api_endpoint=https://localhost:8090/xn"
   ```