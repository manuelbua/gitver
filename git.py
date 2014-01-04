#!/usr/bin/env python2
# coding=utf-8

"""
git support library
"""

import re
import sh
from sh import ErrorReturnCode

version_matcher = r"v{0,1}(\d+)\.(\d+)\.(\d+)-(\d+)-g([a-fA-F0-9]+)"


def git_describe():
    try:
        tagver = sh.git(
            'describe', '--long', '--match=v*').stdout.replace('\n', '')
        vm = re.match(version_matcher, tagver).groups()
        if len(vm) != 5:
            raise AttributeError
    except (ErrorReturnCode, AttributeError):
        print "Error, this repository is required to define tags in the " \
              "format vX.Y.Z"
        return False
    return vm
