=============================================
Avantra Core Ansible Collection Release Notes
=============================================

.. contents:: Topics

v25.2.0
=======

Release Summary
---------------

Release for Avantra 25.2.0 with SOAP API compatibility fixes, improved remote monitoring configuration for SAP systems, and better error handling for server module operations.

Minor Changes
-------------

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
