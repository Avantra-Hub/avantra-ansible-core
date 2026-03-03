# Avantra Core Ansible Collection #

This collection offers core functions to work with Avantra.
You can create, remove servers and SAP systems. Workflows can be executed.

## License ##

[Apache License 2.0](https://github.com/Avantra-Hub/avantra-ansible-core/blob/main/LICENSE)

## Prerequisites

The collection is tested for the following versions of Python and Ansible:

- Ansible version >= 2.16
- Python version >= 3.12

### Matrix  ###

|             | Ansible 2.16 | Ansible 2.17 | Ansible 2.18 | Ansible 2.19 | Ansible 2.20 |
|-------------|--------------|--------------|--------------|--------------|--------------|
| Python 3.13 | unsupported  | unsupported  | tested       | tested       | tested       |
| Python 3.12 | tested       | tested       | tested       | tested       | tested       |

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
ansible-galaxy collection install git+https://github.com/Avantra-Hub/avantra-ansible-core.git,release/25.0.x
```

## Documentation ##

This collection documentation can be found here: https://avantra-hub.github.io/avantra-ansible-core/

## Support ##

For support with this certified Ansible collection, please open an issue at
[Avantra Support](https://support.avantra.com).

For questions about Red Hat Ansible Automation Platform subscriptions, please
contact [Red Hat Support](https://access.redhat.com/support/).

## Release Notes ##

See the [changelog](https://github.com/Avantra-Hub/avantra-ansible-core/blob/main/CHANGELOG.rst).

## References ##

- [Avantra: Documentation](https://docs.avantra.com)
- [Ansible: Developer Guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
