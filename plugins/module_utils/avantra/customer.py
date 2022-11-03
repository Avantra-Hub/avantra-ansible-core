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

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    AvantraAnsibleModule
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (
    cameldict_to_snake_case,
    dict_get
)


def fetch_customer(module, customer_name):
    query = """
    query GetCustomerByName($customer_nameing!) {
        customers(
            where: { filterBy: [{ name: "name", operator: eq, value: $customer_name }] }
        ) {
            id
            name
            sapCustomerNumber
            description
            remarks
            phone
            mobile
            fax
            email
            timezone
            address
            postbox
            postalCode
            city
            country
            timestamp
            customerUrl
            customData
            guid
            parent {
                id
                name
            }
            children {
                id
                name
            }
            childrenCount
        }
    }
    """

    result = module.send_graphql_request(query=query, variables={"customer_name": customer_name})
    customers = dict_get(result, "data", "customers")
    if customers is None or not isinstance(customers, list) or len(customers) == 0:
        return False, "Can not fetch customer: {0}".format(customer_name), None
    else:
        return True, "Successfully fetched customer", cameldict_to_snake_case(customers[0])
