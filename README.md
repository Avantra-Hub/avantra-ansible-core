# Avantra Core Ansible Collection #

This collection offers core functions to work with Avantra.
You can create, remove servers and SAP systems. Workflows can be executed.

## License ##

Apache License 2.0

## Content ##

### Modules ###

| Module Name                     | Description                       |
|---------------------------------|-----------------------------------|
| avantra.core.login              | Avantra authentication operations |
| avantra.core.sapsystem          | manage SAP systems in Avantra     |
| avantra.core.sapsystem_info     | load SAP system information       |
| avantra.core.server             | manage servers in Avantra         |
| avantra.core.server_info        | load server information           |
| avantra.core.workflow_execution | start workflows in Avantra        |

## Usage ##

### Install ###

The avantra.core collection can be either installed using ansible galaxy CLI:

```shell
ansible-galaxy collection install avantra.core
```

or directly from the git repository:

```shell
ansible-galaxy collection install git+https://bitbucket.org/syslink-software/avantra-ansible-core.git,release/23.0.0
```


## References ##

- [Avantra: Documentation](https://docs.avantra.com)
- [Ansible: Developer Guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
