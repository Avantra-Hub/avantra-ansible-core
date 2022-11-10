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

from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (dict_get)

SERVER_START = 20
SERVER_STOP = 21
# SERVER_RESTART = 20
SAP_SYSTEM_START = 1
SAP_SYSTEM_STOP = 2
SAP_SYSTEM_RESTART = 201
SAP_SYSTEM_WITH_DB_START = 32
SAP_SYSTEM_WITH_DB_STOP = 33
SAP_SYSTEM_WITH_DB_RESTART = 202
SAP_SYSTEM_WITH_DB_AND_HANA_START = 34
SAP_SYSTEM_WITH_DB_AND_HANA_STOP = 35
SAP_SYSTEM_WITH_DB_AND_HANA_RESTART = 203
SAP_SYSTEM_WITH_DB_AND_SERVER_START = 36
SAP_SYSTEM_WITH_DB_AND_SERVER_STOP = 37
SAP_SYSTEM_WITH_DB_AND_SERVER_RESTART = 204


def execute_system_action(module, action, system_id, args=None, execution_name=None):

    if args is None:
        args = {}

    variables = {
        "actionId": action,
        "systemIds": [system_id],
        "parameters": [{"key": k, "value": v} for k, v in args.items()]
    }

    if execution_name is not None:
        variables["executionName"] = execution_name

    result = module.send_graphql_request(EXECUTE_ACTION_MUTATION, variables=variables)
    action_result = dict_get(result, "data", "executeSystemAction")

    return action_result


EXECUTE_ACTION_MUTATION = """
            mutation ExecuteSystemAction (
                $actionId: ID!,
                $executionName: String = null,
                $systemIds: [ID!]!,
                $parameters: [SystemActionParameterInput!]!
            ) {
                executeSystemAction(actionId: $actionId,
                    executionName: $executionName,
                    parameter: $parameters,
                    systemIds: $systemIds) {
                        id
                        name
                        description
                        detail
                        status
                        start
                        system {
                            id
                            name
                        }
                        log
                        timestamp
                        user {
                            id
                            principal
                        }
                        customer {
                            id
                            name
                        }
                }

            }
        """
