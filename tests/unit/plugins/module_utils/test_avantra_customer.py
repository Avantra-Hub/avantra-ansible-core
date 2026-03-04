# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock

import pytest

from ansible_collections.avantra.core.plugins.module_utils.avantra.customer import (
    fetch_customer,
)


def _make_module(graphql_response):
    module = MagicMock()
    module.send_graphql_request.return_value = graphql_response
    return module


class TestFetchCustomer:

    def test_fetch_success(self):
        module = _make_module({
            "data": {
                "customers": [{
                    "id": "1",
                    "name": "Acme",
                    "sapCustomerNumber": "12345",
                    "description": "Test customer",
                }]
            }
        })
        success, msg, customer = fetch_customer(module, "Acme")
        assert success is True
        assert customer["id"] == "1"
        assert customer["name"] == "Acme"
        # camelCase → snake_case
        assert "sap_customer_number" in customer
        assert "sapCustomerNumber" not in customer

    def test_fetch_not_found_none(self):
        module = _make_module({"data": {"customers": None}})
        success, msg, customer = fetch_customer(module, "NoSuchCustomer")
        assert success is False
        assert customer is None

    def test_fetch_not_found_empty_list(self):
        module = _make_module({"data": {"customers": []}})
        success, msg, customer = fetch_customer(module, "NoSuchCustomer")
        assert success is False
        assert customer is None

    def test_fetch_not_found_non_list(self):
        module = _make_module({"data": {"customers": "unexpected"}})
        success, msg, customer = fetch_customer(module, "NoSuchCustomer")
        assert success is False
        assert customer is None

    def test_fetch_returns_first_match(self):
        module = _make_module({
            "data": {
                "customers": [
                    {"id": "1", "name": "First"},
                    {"id": "2", "name": "Second"},
                ]
            }
        })
        success, msg, customer = fetch_customer(module, "First")
        assert success is True
        assert customer["id"] == "1"
