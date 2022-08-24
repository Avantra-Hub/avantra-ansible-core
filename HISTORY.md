# HISTORY: Ansible Avantra Core Collection #

## Create a collection ##

- https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_creating.html

```shell
$ mkdir -p ansible-avantra-module
$ cd ansible-avantra-module
$ ansible-galaxy collection init avantra.core
$ cd avantra/core
# From documentation: if Git is used for version control, the corresponding repository should be initialized in the collection directory.
$ git init . 
$ git remote add origin git@bitbucket.org:syslink-software/ansible-module.git
$ git add .
$ git commit -m "Initial commit"
$ git pull origin main
$ git push origin main
```

