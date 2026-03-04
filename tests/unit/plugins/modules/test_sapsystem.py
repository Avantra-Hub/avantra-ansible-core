# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.avantra.core.plugins.modules.sapsystem import (
    ensure_sapsystem_monitoring,
)


class TestEnsureSapsystemMonitoring:

    def _make_module(self, monitoring=None):
        module = MagicMock()
        module.params = {"monitoring": monitoring}
        return module

    # -- monitoring param is None (not requested) → no-op ----------------

    def test_monitoring_none_no_change(self):
        module = self._make_module(monitoring=None)
        sap_system = {"id": "1", "monitor_off": False}
        result = {"changed": False}
        ret = ensure_sapsystem_monitoring(module, sap_system, result)
        assert result["changed"] is False
        assert ret["monitor_off"] is False

    # -- monitoring=False, system currently ON (monitor_off=False) --------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.sapsystem.turn_monitoring_off",
        return_value=(True, "ok", {"id": "1", "monitor_off": True}),
    )
    def test_turn_monitoring_off_from_on(self, mock_off):
        module = self._make_module(monitoring=False)
        sap_system = {"id": "1", "monitor_off": False}
        result = {"changed": False}
        ret = ensure_sapsystem_monitoring(module, sap_system, result)
        mock_off.assert_called_once_with(module, "1")
        assert result["changed"] is True
        assert ret["monitor_off"] is True

    # -- monitoring=True, system currently OFF (monitor_off=True) ---------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.sapsystem.turn_monitoring_on",
        return_value=(True, "ok", {"id": "1", "monitor_off": False}),
    )
    def test_turn_monitoring_on_from_off(self, mock_on):
        module = self._make_module(monitoring=True)
        sap_system = {"id": "1", "monitor_off": True}
        result = {"changed": False}
        ret = ensure_sapsystem_monitoring(module, sap_system, result)
        mock_on.assert_called_once_with(module, "1")
        assert result["changed"] is True
        assert ret["monitor_off"] is False

    # -- monitor_off as string "true" ------------------------------------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.sapsystem.turn_monitoring_on",
        return_value=(True, "ok", {"id": "1", "monitor_off": False}),
    )
    def test_monitor_off_string_true(self, mock_on):
        module = self._make_module(monitoring=True)
        sap_system = {"id": "1", "monitor_off": "true"}
        result = {"changed": False}
        ret = ensure_sapsystem_monitoring(module, sap_system, result)
        mock_on.assert_called_once_with(module, "1")
        assert result["changed"] is True
        assert ret["monitor_off"] is False

    # -- already in desired state → no-op --------------------------------

    def test_monitoring_on_already_on_no_change(self):
        module = self._make_module(monitoring=True)
        sap_system = {"id": "1", "monitor_off": False}
        result = {"changed": False}
        ret = ensure_sapsystem_monitoring(module, sap_system, result)
        assert result["changed"] is False

    def test_monitoring_off_already_off_no_change(self):
        module = self._make_module(monitoring=False)
        sap_system = {"id": "1", "monitor_off": True}
        result = {"changed": False}
        ret = ensure_sapsystem_monitoring(module, sap_system, result)
        assert result["changed"] is False

    # -- API call fails → changed stays False ----------------------------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.sapsystem.turn_monitoring_off",
        return_value=(False, "API error", None),
    )
    def test_monitoring_off_api_failure_no_change(self, mock_off):
        module = self._make_module(monitoring=False)
        sap_system = {"id": "1", "monitor_off": False}
        result = {"changed": False}
        ret = ensure_sapsystem_monitoring(module, sap_system, result)
        assert result["changed"] is False
        assert ret["monitor_off"] is False

    # -- monitor_off key missing → defaults to False (monitoring ON) ------

    @patch(
        "ansible_collections.avantra.core.plugins.modules.sapsystem.turn_monitoring_off",
        return_value=(True, "ok", {"id": "1", "monitor_off": True}),
    )
    def test_monitor_off_key_missing_defaults_to_on(self, mock_off):
        module = self._make_module(monitoring=False)
        sap_system = {"id": "1"}
        result = {"changed": False}
        ret = ensure_sapsystem_monitoring(module, sap_system, result)
        mock_off.assert_called_once_with(module, "1")
        assert result["changed"] is True
        assert ret["monitor_off"] is True
