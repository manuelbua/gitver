#!/usr/bin/env python2
# coding=utf-8

"""
Simple version string management for git
"""

__license__ = """
Copyright (c) 2013-2014 Manuel Bua.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

__author__ = "Manuel Bua"

try:
    from version import gitver_version
    __version__ = gitver_version
except ImportError:
    __version__ = 'UNKNOWN'
