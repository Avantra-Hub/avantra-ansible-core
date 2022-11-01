# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    RETURN = r"""
sap_system:
    description: The SAP system if it was found.
    type: dict
    returned: success
    sample: 
        sap_system:
            administrator:
            administrator_deputy:
            application_type: Generic
            assigned_sla:
            avantra_transport_version: 23.0.0.0
            basis_release: '7.40'
            check_count: 0
            component_version:
            credentials:
                - id: avantra.sapControl
                  password: ropeGO01
                  private_key:
                  private_key_passphrase:
                  purpose:
                      id: "-7"
                      key: sapControl
                      name: SAP Control User
                  sap_control_user: smaadm
                - id: avantra.sap
                  password: aaaa
                  purpose:
                      id: '5'
                      key: sap
                      name: SAP
                  rfc_user: aaaa
                - basic_user: sapsa
                  id: avantra.abapDbSchema
                  password: ropeGO01
                  purpose:
                      id: "-4"
                      key: abapDbSchema
                      name: ABAP DB Schema User
            custom_attributes: []
            custom_data:
            customer:
                id: '4'
                name: mis
            database:
                database_type: SAP_SYBASE_ASE
                dbms_product: SYBASE 16.0.03.09
                id: sapdb-5
                name: SMA
                server:
                    id: '1'
                    name: achnmc-mis
                version: 16.0.03.09
            database_host: golf
            database_monitoring_server:
                id: '1'
                name: achnmc-mis
            database_name: SMA
            database_port: 4901
            database_release: '16.0'
            database_type: SAP ASE
            default_client:
            description: ''
            encoding: U2L
            id: '5'
            maintenance: false
            monitor_level: AUTHENTICATED
            monitor_off: false
            monitor_off_until:
            monitor_switch_date:
            monitor_switch_reason:
            mst: 2
            name: SMA_REMOTE
            operational: true
            operational_since:
            operational_until:
            product_versions:
                - product: SAP SOLUTION MANAGER
                  release: '7.2'
                  short_description: SAP SOLUTION MANAGER 7.2
                  sp_stack: 13 (08/2021) FPS
                  status: INSTALLED
                - product: SLT
                  release: '2.0'
                  short_description: SAP LT REPLICATION SERVER 2.0
                  sp_stack: SP13 (06/2017) SP
                  status: INSTALLED
            real_sap_sid: SMA
            remote: true
            remote_monitoring_server:
                id: '1'
                name: achnmc-mis
            sap_instances_count: 2
            solution_manager:
            spam_patch_level: 740/0082
            status: OK
            status_id: 0
            system_role: Development
            timestamp: '2022-10-12T14:32:27.000+02:00'
            timezone:
            type: SAP_SYSTEM
            unified_sap_sid: SMA_REMOTE
            uuid: 3e7f6884-0bde-46b0-825b-3090df258675
"""
