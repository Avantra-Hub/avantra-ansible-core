# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    AvantraAnsibleModule
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (
    cameldict_to_snake_case,
    dict_get
)


def fetch_customer(module: AvantraAnsibleModule, customer_name: str) -> (bool, str, dict):
    query = """
    query GetCustomerByName($customer_name: String!) {
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
        return False, "Can not fetch customer: {}".format(customer_name), None
    else:
        return True, "Successfully fetched customer", cameldict_to_snake_case(customers[0])
