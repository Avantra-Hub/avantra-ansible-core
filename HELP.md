# DEVELOPMENT NOTES

## Build

```shell
ansible-galaxy collection build --force
ansible-galaxy collection install avantra-core-25.2.0.tar.gz --force    
```

## Test playbooks (tests/*.yml)

```shell
cd tests
ansible-vault create secrets.yml
# enter password -> vi opens enter secrets
# avantra_api_user:
# avantra_api_password:
# and SAVE

```

secrets.yml wil not be committed to git as it is entered in .gitignore!

to run the test use the command:

```shell
ansible-playbook playbook_file.yml --ask-vault-pass
```