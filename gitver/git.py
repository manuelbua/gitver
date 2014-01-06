#!/usr/bin/env python2
# coding=utf-8

"""
git support library
"""

import sys
import re
from gitver.termcolors import err

try:
    import sh
    from sh import ErrorReturnCode
except ImportError:
    print "A dependency is missing, please install the \"sh\" package and " \
          "run gitver again."
    sys.exit(1)

version_matcher = r"v{0,1}(\d+)\.(\d+)\.(\d+)-(\d+)-g([a-fA-F0-9]+)"


def project_root():
    try:
        root = sh.git('rev-parse', '--show-toplevel').stdout.replace('\n', '')
    except ErrorReturnCode:
        return ''
    return root


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
        print err("Error, this repository is required to define tags in the "
                  "format vX.Y.Z")
        sys.exit(1)

    # extract version string, assumes HEAD to be at that commit
    vmaj = int(desc[0])
    vmin = int(desc[1])
    vpatch = int(desc[2])
    vcount = int(desc[3])
    vhash = desc[4]
    hashlen = len(vhash)
    full_build_id = get_build_id()
    if not full_build_id or hashlen == 0:
        print err("Couldn't retrieve build id information")
        sys.exit(1)

    # sanity check
    if not full_build_id.startswith(vhash):
        print err("Hash problem detected: git-describe reports " + vhash +
                  ", but HEAD id is " + full_build_id)
        sys.exit(1)

    tag = last_tag()
    if not tag:
        print err("Couldn't retrieve the latest tag")
        sys.exit(1)

    return {'maj': vmaj, 'min': vmin, 'patch': vpatch, 'count': vcount,
            'build-id': full_build_id[:hashlen], 'full-build-id': full_build_id,
            'last-tag': tag}
