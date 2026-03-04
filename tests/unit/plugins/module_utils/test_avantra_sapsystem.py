# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock

from ansible_collections.avantra.core.plugins.module_utils.avantra.sapsystem import (
    fetch_sapsystem,
    delete_sapsystem,
    turn_monitoring_off,
    turn_monitoring_on,
)


def _make_module(graphql_response):
    module = MagicMock()
    module.send_graphql_request.return_value = graphql_response
    return module


# ---------------------------------------------------------------------------
# fetch_sapsystem
# ---------------------------------------------------------------------------

class TestFetchSapsystem:

    def test_fetch_success(self):
        module = _make_module({
            "data": {
                "systems": [{
                    "id": "10",
                    "unifiedSapSid": "DEV",
                    "realSapSid": "DEV",
                    "monitorOff": False,
                    "customer": {"id": "1", "name": "Acme"},
                    "checks": [],
                }]
            }
        })
        success, msg, sap = fetch_sapsystem(module, unified_sap_sid="DEV", customer_name="Acme")
        assert success is True
        assert sap["id"] == "10"
        assert sap["unified_sap_sid"] == "DEV"
        assert "monitor_off" in sap
        assert "monitorOff" not in sap

    def test_fetch_not_found_none(self):
        module = _make_module({"data": {"systems": None}})
        success, msg, sap = fetch_sapsystem(module, unified_sap_sid="X", customer_name="Acme")
        assert success is False
        assert sap is None

    def test_fetch_not_found_empty(self):
        module = _make_module({"data": {"systems": []}})
        success, msg, sap = fetch_sapsystem(module, unified_sap_sid="X", customer_name="Acme")
        assert success is False
        assert sap is None

    def test_fetch_remove_checks(self):
        module = _make_module({
            "data": {
                "systems": [{
                    "id": "10",
                    "unifiedSapSid": "DEV",
                    "checks": [{"id": "1"}],
                }]
            }
        })
        success, msg, sap = fetch_sapsystem(
            module, unified_sap_sid="DEV", customer_name="Acme", remove_checks=True
        )
        assert success is True
        assert "checks" not in sap


# ---------------------------------------------------------------------------
# delete_sapsystem
# ---------------------------------------------------------------------------

class TestDeleteSapsystem:

    def test_delete_success(self):
        module = _make_module({
            "data": {
                "deleteSapSystem": {
                    "result": {"success": True, "message": "Deleted", "code": None}
                }
            }
        })
        success, msg = delete_sapsystem(module, "10")
        assert success is True

    def test_delete_failure(self):
        module = _make_module({
            "data": {
                "deleteSapSystem": {
                    "result": {"success": False, "message": "Not found", "code": "404"}
                }
            }
        })
        success, msg = delete_sapsystem(module, "999")
        assert success is False
        assert msg == "Not found"

    def test_delete_null_result(self):
        module = _make_module({"data": {"deleteSapSystem": None}})
        success, msg = delete_sapsystem(module, "999")
        assert success is False


# ---------------------------------------------------------------------------
# turn_monitoring_off / on
# ---------------------------------------------------------------------------

class TestTurnMonitoringOff:

    def test_success_returns_snake_case(self):
        module = _make_module({
            "data": {
                "turnMonitoringOffForSapSystem": {
                    "id": "10",
                    "monitorOff": True,
                    "monitorSwitchReason": "API",
                }
            }
        })
        success, msg, sap = turn_monitoring_off(module, "10")
        assert success is True
        assert sap["monitor_off"] is True
        assert "monitorOff" not in sap

    def test_failure_returns_none(self):
        module = _make_module({"data": {"turnMonitoringOffForSapSystem": None}})
        success, msg, sap = turn_monitoring_off(module, "10")
        assert success is False
        assert sap is None


class TestTurnMonitoringOn:

    def test_success_returns_snake_case(self):
        module = _make_module({
            "data": {
                "turnMonitoringOnForSapSystem": {
                    "id": "10",
                    "monitorOff": False,
                    "monitorSwitchReason": "API",
                }
            }
        })
        success, msg, sap = turn_monitoring_on(module, "10")
        assert success is True
        assert sap["monitor_off"] is False
        assert "monitorOff" not in sap

    def test_failure_returns_none(self):
        module = _make_module({"data": {"turnMonitoringOnForSapSystem": None}})
        success, msg, sap = turn_monitoring_on(module, "10")
        assert success is False
        assert sap is None
