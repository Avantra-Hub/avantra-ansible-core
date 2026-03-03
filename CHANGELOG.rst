=============================================
Avantra Core Ansible Collection Release Notes
=============================================

.. contents:: Topics

v25.3.0
=======

Release Summary
---------------

Release for Red Hat Automation Hub certification. Updates minimum Ansible requirement to 2.16.0, adds Support section to README, and includes automated Automation Hub publishing. Also includes SOAP API compatibility fixes, improved remote monitoring for SAP systems, and better server module error handling.

Minor Changes
-------------

- collection - Update ``requires_ansible`` to ``>=2.16.0`` for Red Hat Automation Hub certification compliance.
- collection - Add Support and Release Notes sections to README per Red Hat certified collection requirements.
- collection - Add automated publishing to Red Hat Automation Hub in release workflow.
- collection - Remove Python 3.10 and 3.11 from test matrix, require Python >=3.12.
- sapsystem - Support ``withSapControl`` and ``withoutSapControl`` remote monitoring modes.
- sapsystem - Use new ``remoteOptions`` API structure for remote monitoring configuration, replacing the flat ``remoteMonitoringEntryPoint`` and ``remoteMonitoringServerSystemId`` fields.
- server - Add log message on successful server creation.
- server - Improve error messages for missing ``system_role`` and ``fqdn_or_ip_address`` arguments during server creation.

Bugfixes
--------

- api - Remove ``soapenv:mustUnderstand`` attribute from SOAP security header to fix compatibility issues.
- sapsystem - Disable ``monitoring`` field in SAP system update to prevent unintended changes.
- server - Disable ``monitoring`` field in server update to prevent unintended changes.

v24.0.0
=======

Release Summary
---------------

This version of the collection was released to support the Ansible versions: 2.14, 2.15, 2.16

v23.0.2
=======

Release Summary
---------------

This release fixed some minor bugs.
