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

CLOUD_SERVICE_NAME = "CLOUD_SERVICE"
SAP_BUSINESS_OBJECT_NAME = "SAP_BUSINESS_OBJECT"
BUSINESS_SERVICE_NAME = "BUSINESS_SERVICE"
DATABASE_NAME = "DATABASE"
SAP_SYSTEM_NAME = "SAP_SYSTEM"
SAP_INSTANCE_NAME = "SAP_INSTANCE"
SERVER_NAME = "SERVER"

CLOUD_SERVICE_ID = 6
SAP_BUSINESS_OBJECT_ID = 5
BUSINESS_SERVICE_ID = 4
DATABASE_ID = 3
SAP_SYSTEM_ID = 2
SAP_INSTANCE_ID = 1
SERVER_ID = 0


class SystemType(object):
    """
    Simple class to handle monitored system types.
    """

    def __init__(self, name, value):
        self.__name = name
        self.__value = value

    def name(self):
        return self.__name

    def value(self):
        return self.__value


SERVER = SystemType(SERVER_NAME, SERVER_ID)
SAP_INSTANCE = SystemType(SAP_INSTANCE_NAME, SAP_INSTANCE_ID)
SAP_SYSTEM = SystemType(SAP_SYSTEM_NAME, SAP_SYSTEM_ID)
DATABASE = SystemType(DATABASE_NAME, DATABASE_ID)
BUSINESS_SERVICE = SystemType(BUSINESS_SERVICE_NAME, BUSINESS_SERVICE_ID)
SAP_BUSINESS_OBJECT = SystemType(SAP_BUSINESS_OBJECT_NAME, SAP_BUSINESS_OBJECT_ID)
CLOUD_SERVICE = SystemType(CLOUD_SERVICE_NAME, CLOUD_SERVICE_ID)


def type_of_name(name):
    """
    Returns a system type given its name.
    :param name: the name of the system type.
    :return: a valid SystemType instance
    """
    if name == SERVER_NAME:
        return SERVER
    elif name == SAP_INSTANCE_NAME:
        return SAP_INSTANCE
    elif name == SAP_SYSTEM_NAME:
        return SAP_SYSTEM
    elif name == DATABASE_NAME:
        return DATABASE
    elif name == BUSINESS_SERVICE_NAME:
        return BUSINESS_SERVICE
    elif name == SAP_BUSINESS_OBJECT_NAME:
        return SAP_BUSINESS_OBJECT
    elif name == CLOUD_SERVICE_NAME:
        return CLOUD_SERVICE
    else:
        raise AssertionError("Unknown system type name: {0}".format(name))


def type_of_value(value):
    """
    Returns a system type given its value.
    :param value: the value of the system type.
    :return: a valid SystemType instance
    """
    if value == SERVER_ID:
        return SERVER
    elif value == SAP_INSTANCE_ID:
        return SAP_INSTANCE
    elif value == SAP_SYSTEM_ID:
        return SAP_SYSTEM
    elif value == DATABASE_ID:
        return DATABASE
    elif value == BUSINESS_SERVICE_ID:
        return BUSINESS_SERVICE
    elif value == SAP_BUSINESS_OBJECT_ID:
        return SAP_BUSINESS_OBJECT
    elif value == CLOUD_SERVICE_ID:
        return CLOUD_SERVICE
    else:
        raise AssertionError("Unknown system type id: {0}".format(value))


def type_of(value):
    """
    Returns the SystemType for the given value.
    :param value: an object identifying a system type. Either a string or a number.
    :return: a valid SystemType instance
    """
    if isinstance(value, str):
        return type_of_name(value)
    elif isinstance(value, int):
        return type_of_value(value)
    else:
        raise AssertionError("Unknown type to identify a system type: {0}".format(value))
