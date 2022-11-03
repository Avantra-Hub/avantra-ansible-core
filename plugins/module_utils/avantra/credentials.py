# -*- coding: utf-8 -*-

# Copyright 2022 Avantra

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from enum import Enum

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    AvantraAnsibleModule
)


class CredentialType(Enum):
    BASIC = 0
    OAUTH2_CODE = 1
    OAUTH2_CLIENT = 2
    RFC = 3
    SAP_CONTROL = 4
    SSH = 5


def handle_basic_credentials(basic_creds, key, cred):
    basic_creds.append({
        "id": key,
        "username": cred.get("username"),
        "password": cred.get("password"),
        "name": cred.get("name"),
        # "shared": cred.get("shared")
    })


def handle_ssh_credentials(ssh_creds, key, cred):
    config = []
    for k, v in cred.get("config", {}).items():
        config.append({
            "key": k,
            "value": v
        })

    ssh_creds.append({
        "id": key,
        "username": cred.get("username"),
        "password": cred.get("password"),
        "hostname": cred.get("hostname"),
        "port": cred.get("port"),
        # TODO: maybe this is a path read the file???
        "identity": cred.get("identity"),
        "identityPassphrase": cred.get("identityPassphrase"),
        "config": config
    })


def handle_sap_control_credentials(sap_control_creds, key, cred):
    sap_control_creds.append({
        "id": key,
        "username": cred.get("username"),
        "password": cred.get("password"),
        "privateKey": cred.get("private_key"),
        "privateKeyPassphrase": cred.get("private_key_passphrase"),
        "certificateChain": cred.get("certificate_chain"),
        "name": cred.get("name"),
        # "shared": cred.get("shared")
    })


def handle_rfc_credentials(rfc_creds, key, cred):
    rfc_creds.append({
        "id": key,
        "username": cred.get("username"),
        "password": cred.get("password"),
        "client": cred.get("client"),
        "name": cred.get("name"),
        # "shared": cred.get("shared")
    })


def handle_oauth_client_credentials(oauth_client_creds, key, cred):
    pass


def handle_oauth_code_credentials(oauth_code_creds, key, cred):
    pass


def handle_credentials(module, credentials):
    """
    Given a credentials dictionary this function converts the found credential information in dicts that the
    GraphQL API can understand.
    :param module:
    :param credentials:
    :return:
    """
    basic_creds = []
    ssh_creds = []
    sap_control_creds = []
    rfc_creds = []
    oauth_client_creds = []
    oauth_code_creds = []
    if credentials is not None and len(credentials) > 0:
        for key, cred in credentials.items():
            if "cred_type" in cred:
                cred_type = str(cred["cred_type"]).upper()
                if cred_type == CredentialType.BASIC.name:
                    handle_basic_credentials(basic_creds, key, cred)
                elif cred_type == CredentialType.SSH.name:
                    handle_ssh_credentials(ssh_creds, key, cred)
                elif cred_type == CredentialType.SAP_CONTROL.name:
                    handle_sap_control_credentials(sap_control_creds, key, cred)
                elif cred_type == CredentialType.RFC.name:
                    handle_rfc_credentials(rfc_creds, key, cred)
                # elif cred_type == CredentialType.OAUTH2_CLIENT.name:
                #     handle_oauth_client_credentials(oauth_client_creds, key, cred)
                # elif cred_type == CredentialType.OAUTH2_CODE.name:
                #     handle_oauth_code_credentials(oauth_code_creds, key, cred)
                else:
                    module.fail_json(msg="Unhandled credential type '{0}'".format(cred_type))
            else:
                module.fail_json(msg="No cred_type defined for credentials with key '{0}'".format(key))

    return {
        CredentialType.BASIC: basic_creds,
        CredentialType.SSH: ssh_creds,
        CredentialType.SAP_CONTROL: sap_control_creds,
        CredentialType.RFC: rfc_creds,
        CredentialType.OAUTH2_CLIENT: oauth_client_creds,
        CredentialType.OAUTH2_CODE: oauth_code_creds
    }
