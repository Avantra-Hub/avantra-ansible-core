# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.avantra.core.plugins.modules.server import (
    ensure_server_monitoring,
    _get_server_run_state,
)


# ---------------------------------------------------------------------------
# _get_server_run_state
# ---------------------------------------------------------------------------

class TestGetServerRunState:

    def test_none_server_returns_unknown(self):
        assert _get_server_run_state(None) == "unknown"

    def test_empty_checks_returns_unknown(self):
        server = {"checks": []}
        assert _get_server_run_state(server) == "unknown"

    def test_checks_without_last_refresh_attr_returns_unknown(self):
        """checks[0] is a dict, not an object with attributes, so hasattr fails."""
        server = {"checks": [{"name": "AGENTALIVE", "status": "OK"}]}
        assert _get_server_run_state(server) == "unknown"

    def test_checks_popped_from_server(self):
        server = {"checks": [{"name": "AGENTALIVE"}]}
        _get_server_run_state(server)
        assert "checks" not in server


# ---------------------------------------------------------------------------
# ensure_server_monitoring
# ---------------------------------------------------------------------------

class TestEnsureServerMonitoring:

    def _make_module(self, monitoring=None):
        module = MagicMock()
        module.params = {"monitoring": monitoring}
        return module

    # -- monitoring param is None (not requested) → no-op ----------------

    def test_monitoring_none_no_change(self):
        module = self._make_module(monitoring=None)
        server = {"id": "1", "monitor_off": False}
        result = {"changed": False}
        ret = ensure_server_monitoring(module, server, result)
        assert result["changed"] is False
        assert ret["monitor_off"] is False

    # -- monitoring=False, server currently ON (monitor_off=False) --------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.server.turn_monitoring_off",
        return_value=(True, "ok", {"id": "1", "monitor_off": True}),
    )
    def test_turn_monitoring_off_from_on(self, mock_off):
        module = self._make_module(monitoring=False)
        server = {"id": "1", "monitor_off": False}
        result = {"changed": False}
        ret = ensure_server_monitoring(module, server, result)
        mock_off.assert_called_once_with(module, "1")
        assert result["changed"] is True
        assert ret["monitor_off"] is True

    # -- monitoring=True, server currently OFF (monitor_off=True) ---------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.server.turn_monitoring_on",
        return_value=(True, "ok", {"id": "1", "monitor_off": False}),
    )
    def test_turn_monitoring_on_from_off(self, mock_on):
        module = self._make_module(monitoring=True)
        server = {"id": "1", "monitor_off": True}
        result = {"changed": False}
        ret = ensure_server_monitoring(module, server, result)
        mock_on.assert_called_once_with(module, "1")
        assert result["changed"] is True
        assert ret["monitor_off"] is False

    # -- monitor_off as string "true" (API sometimes returns strings) -----

    @patch(
        "ansible_collections.avantra.core.plugins.modules.server.turn_monitoring_on",
        return_value=(True, "ok", {"id": "1", "monitor_off": False}),
    )
    def test_monitor_off_string_true(self, mock_on):
        module = self._make_module(monitoring=True)
        server = {"id": "1", "monitor_off": "true"}
        result = {"changed": False}
        ret = ensure_server_monitoring(module, server, result)
        mock_on.assert_called_once_with(module, "1")
        assert result["changed"] is True
        assert ret["monitor_off"] is False

    # -- monitoring=True, already ON → no-op -----------------------------

    def test_monitoring_on_already_on_no_change(self):
        module = self._make_module(monitoring=True)
        server = {"id": "1", "monitor_off": False}
        result = {"changed": False}
        ret = ensure_server_monitoring(module, server, result)
        assert result["changed"] is False

    # -- monitoring=False, already OFF → no-op ---------------------------

    def test_monitoring_off_already_off_no_change(self):
        module = self._make_module(monitoring=False)
        server = {"id": "1", "monitor_off": True}
        result = {"changed": False}
        ret = ensure_server_monitoring(module, server, result)
        assert result["changed"] is False

    # -- API call fails → changed stays False ----------------------------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.server.turn_monitoring_off",
        return_value=(False, "API error", None),
    )
    def test_monitoring_off_api_failure_no_change(self, mock_off):
        module = self._make_module(monitoring=False)
        server = {"id": "1", "monitor_off": False}
        result = {"changed": False}
        ret = ensure_server_monitoring(module, server, result)
        assert result["changed"] is False
        # monitor_off should NOT have been updated
        assert ret["monitor_off"] is False

    # -- monitor_off missing from server dict (defaults to False) --------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.server.turn_monitoring_off",
        return_value=(True, "ok", {"id": "1", "monitor_off": True}),
    )
    def test_monitor_off_key_missing_defaults_to_on(self, mock_off):
        module = self._make_module(monitoring=False)
        server = {"id": "1"}  # no monitor_off key
        result = {"changed": False}
        ret = ensure_server_monitoring(module, server, result)
        mock_off.assert_called_once_with(module, "1")
        assert result["changed"] is True
        assert ret["monitor_off"] is True
