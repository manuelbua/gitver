#!/usr/bin/env python2
# coding=utf-8

"""
git support library
"""

import sys
import re
import sh
from sh import ErrorReturnCode

version_matcher = r"v{0,1}(\d+)\.(\d+)\.(\d+)-(\d+)-g([a-fA-F0-9]+)"


def describe():
    try:
        tagver = sh.git(
            'describe', '--long', '--match=v*').stdout.replace('\n', '')
        vm = re.match(version_matcher, tagver).groups()
        if len(vm) != 5:
            raise AttributeError
    except (ErrorReturnCode, AttributeError):
        return False
    return vm


def get_build_id():
    try:
        full_build_id = str(
            sh.git('rev-parse', 'HEAD').stdout.replace('\n', ''))
    except ErrorReturnCode:
        return False
    return full_build_id


def last_tag():
    try:
        tag = sh.git('describe', '--abbrev=0').stdout.replace('\n', '')
    except ErrorReturnCode:
        return False

    return tag


def get_repo_info():
    # retrieve basic repository information
    desc = describe()
    if not desc:
        print "Error, this repository is required to define tags in the " \
              "format vX.Y.Z"
        sys.exit(1)

    # extract version string
    vmaj = int(desc[0])
    vmin = int(desc[1])
    vpatch = int(desc[2])
    vcount = int(desc[3])
    vhash = desc[4]

    full_build_id = get_build_id()
    if not full_build_id:
        print "Couldn't retrieve build id information"
        sys.exit(1)

    # sanity check
    if not full_build_id.startswith(vhash):
        print "Hash problem detected: git describe reports " + vhash + \
              ", but full id is " + full_build_id

    tag = last_tag()
    if not tag:
        print "Couldn't retrieve the latest tag"
        sys.exit(1)

    return {'maj': vmaj, 'min': vmin, 'patch': vpatch, 'count': vcount,
            'build-id': full_build_id[:8], 'full-build-id': full_build_id,
            'last-tag': tag}
