# -*- coding: utf-8 -*-

# Copyright Avantra

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

import pytest
from ansible_collections.avantra.core.plugins.module_utils.avantra.mst import (
    SERVER_NAME,
    SERVER_ID,
    SERVER,
    SAP_INSTANCE_NAME,
    SAP_INSTANCE_ID,
    SAP_INSTANCE,
    SAP_SYSTEM_NAME,
    SAP_SYSTEM_ID,
    SAP_SYSTEM,
    DATABASE_NAME,
    DATABASE_ID,
    DATABASE,
    BUSINESS_SERVICE_NAME,
    BUSINESS_SERVICE_ID,
    BUSINESS_SERVICE,
    SAP_BUSINESS_OBJECT_NAME,
    SAP_BUSINESS_OBJECT_ID,
    SAP_BUSINESS_OBJECT,
    CLOUD_SERVICE_NAME,
    CLOUD_SERVICE_ID,
    CLOUD_SERVICE,
    type_of,
    type_of_name,
    type_of_value
)


def test_values():
    assert SERVER_ID == 0
    assert SAP_INSTANCE_ID == 1
    assert SAP_SYSTEM_ID == 2
    assert DATABASE_ID == 3
    assert BUSINESS_SERVICE_ID == 4
    assert SAP_BUSINESS_OBJECT_ID == 5
    assert CLOUD_SERVICE_ID == 6


def test_names():
    assert SERVER_NAME == "SERVER"
    assert SAP_INSTANCE_NAME == "SAP_INSTANCE"
    assert SAP_SYSTEM_NAME == "SAP_SYSTEM"
    assert DATABASE_NAME == "DATABASE"
    assert BUSINESS_SERVICE_NAME == "BUSINESS_SERVICE"
    assert SAP_BUSINESS_OBJECT_NAME == "SAP_BUSINESS_OBJECT"
    assert CLOUD_SERVICE_NAME == "CLOUD_SERVICE"


def test_type_of_name():
    assert type_of_name(SERVER_NAME) == SERVER
    assert type_of_name(SAP_INSTANCE_NAME) == SAP_INSTANCE
    assert type_of_name(SAP_SYSTEM_NAME) == SAP_SYSTEM
    assert type_of_name(DATABASE_NAME) == DATABASE
    assert type_of_name(BUSINESS_SERVICE_NAME) == BUSINESS_SERVICE
    assert type_of_name(SAP_BUSINESS_OBJECT_NAME) == SAP_BUSINESS_OBJECT
    assert type_of_name(CLOUD_SERVICE_NAME) == CLOUD_SERVICE
    with pytest.raises(AssertionError):
        type_of_name(None)
    with pytest.raises(AssertionError):
        type_of_name(43)
    with pytest.raises(AssertionError):
        type_of_name("WRONG_NAME")


def test_type_of_value():
    assert type_of_value(SERVER_ID) == SERVER
    assert type_of_value(SAP_INSTANCE_ID) == SAP_INSTANCE
    assert type_of_value(SAP_SYSTEM_ID) == SAP_SYSTEM
    assert type_of_value(DATABASE_ID) == DATABASE
    assert type_of_value(BUSINESS_SERVICE_ID) == BUSINESS_SERVICE
    assert type_of_value(SAP_BUSINESS_OBJECT_ID) == SAP_BUSINESS_OBJECT
    assert type_of_value(CLOUD_SERVICE_ID) == CLOUD_SERVICE
    with pytest.raises(AssertionError):
        type_of_value(None)
    with pytest.raises(AssertionError):
        type_of_value(43)
    with pytest.raises(AssertionError):
        type_of_value("WRONG_NAME")


def test_type_of():
    assert type_of(SERVER_ID) == SERVER
    assert type_of(SAP_INSTANCE_ID) == SAP_INSTANCE
    assert type_of(SAP_SYSTEM_ID) == SAP_SYSTEM
    assert type_of(DATABASE_ID) == DATABASE
    assert type_of(BUSINESS_SERVICE_ID) == BUSINESS_SERVICE
    assert type_of(SAP_BUSINESS_OBJECT_ID) == SAP_BUSINESS_OBJECT
    assert type_of(CLOUD_SERVICE_ID) == CLOUD_SERVICE

    assert type_of(SERVER_NAME) == SERVER
    assert type_of(SAP_INSTANCE_NAME) == SAP_INSTANCE
    assert type_of(SAP_SYSTEM_NAME) == SAP_SYSTEM
    assert type_of(DATABASE_NAME) == DATABASE
    assert type_of(BUSINESS_SERVICE_NAME) == BUSINESS_SERVICE
    assert type_of(SAP_BUSINESS_OBJECT_NAME) == SAP_BUSINESS_OBJECT
    assert type_of(CLOUD_SERVICE_NAME) == CLOUD_SERVICE

    with pytest.raises(AssertionError):
        type_of(None)
    with pytest.raises(AssertionError):
        type_of(43)
    with pytest.raises(AssertionError):
        type_of("WRONG_NAME")
