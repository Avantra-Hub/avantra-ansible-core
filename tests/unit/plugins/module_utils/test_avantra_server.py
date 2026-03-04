# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock

from ansible_collections.avantra.core.plugins.module_utils.avantra.server import (
    fetch_server,
    delete_server,
    turn_monitoring_off,
    turn_monitoring_on,
)


def _make_module(graphql_response):
    module = MagicMock()
    module.send_graphql_request.return_value = graphql_response
    return module


# ---------------------------------------------------------------------------
# fetch_server
# ---------------------------------------------------------------------------

class TestFetchServer:

    def test_fetch_server_success(self):
        module = _make_module({
            "data": {
                "systems": [{
                    "id": "42",
                    "name": "srv01",
                    "monitorOff": False,
                    "customer": {"id": "1", "name": "Acme"},
                    "checks": [],
                }]
            }
        })
        success, msg, server = fetch_server(module, server_name="srv01", customer_name="Acme")
        assert success is True
        assert server["id"] == "42"
        assert server["name"] == "srv01"
        # camelCase → snake_case
        assert "monitor_off" in server
        assert "monitorOff" not in server

    def test_fetch_server_not_found_none(self):
        module = _make_module({"data": {"systems": None}})
        success, msg, server = fetch_server(module, server_name="nope", customer_name="Acme")
        assert success is False
        assert server is None

    def test_fetch_server_not_found_empty(self):
        module = _make_module({"data": {"systems": []}})
        success, msg, server = fetch_server(module, server_name="nope", customer_name="Acme")
        assert success is False
        assert server is None

    def test_fetch_server_remove_checks(self):
        module = _make_module({
            "data": {
                "systems": [{
                    "id": "42",
                    "name": "srv01",
                    "checks": [{"id": "1"}],
                }]
            }
        })
        success, msg, server = fetch_server(
            module, server_name="srv01", customer_name="Acme", remove_checks=True
        )
        assert success is True
        assert "checks" not in server


# ---------------------------------------------------------------------------
# delete_server
# ---------------------------------------------------------------------------

class TestDeleteServer:

    def test_delete_success(self):
        module = _make_module({
            "data": {
                "deleteServer": {
                    "result": {"success": True, "message": "Deleted", "code": None}
                }
            }
        })
        success, msg = delete_server(module, "42")
        assert success is True

    def test_delete_failure(self):
        module = _make_module({
            "data": {
                "deleteServer": {
                    "result": {"success": False, "message": "Not found", "code": "404"}
                }
            }
        })
        success, msg = delete_server(module, "999")
        assert success is False
        assert msg == "Not found"

    def test_delete_null_result(self):
        module = _make_module({"data": {"deleteServer": None}})
        success, msg = delete_server(module, "999")
        assert success is False


# ---------------------------------------------------------------------------
# turn_monitoring_off / on
# ---------------------------------------------------------------------------

class TestTurnMonitoringOff:

    def test_success_returns_snake_case(self):
        module = _make_module({
            "data": {
                "turnMonitoringOffForServer": {
                    "id": "42",
                    "monitorOff": True,
                    "monitorSwitchReason": "API",
                }
            }
        })
        success, msg, server = turn_monitoring_off(module, "42")
        assert success is True
        assert server["monitor_off"] is True
        assert "monitor_switch_reason" in server
        assert "monitorOff" not in server

    def test_failure_returns_none(self):
        module = _make_module({"data": {"turnMonitoringOffForServer": None}})
        success, msg, server = turn_monitoring_off(module, "42")
        assert success is False
        assert server is None


class TestTurnMonitoringOn:

    def test_success_returns_snake_case(self):
        module = _make_module({
            "data": {
                "turnMonitoringOnForServer": {
                    "id": "42",
                    "monitorOff": False,
                    "monitorSwitchReason": "API",
                }
            }
        })
        success, msg, server = turn_monitoring_on(module, "42")
        assert success is True
        assert server["monitor_off"] is False
        assert "monitorOff" not in server

    def test_failure_returns_none(self):
        module = _make_module({"data": {"turnMonitoringOnForServer": None}})
        success, msg, server = turn_monitoring_on(module, "42")
        assert success is False
        assert server is None
