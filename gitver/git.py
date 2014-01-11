#!/usr/bin/env python2
# coding=utf-8

"""
git support library
"""

import sys
import re
from gitver.termcolors import err

# check for the sh package
try:
    import sh
    from sh import ErrorReturnCode, CommandNotFound
except ImportError:
    print "A dependency is missing, please install the \"sh\" package and " \
          "run gitver again."
    sys.exit(1)

hash_matcher = r".*-g([a-fA-F0-9]+)"
tag_matcher = r"v{0,1}(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-.]*))?"


def git_version():
    try:
        ver = sh.git('--version').stdout.replace('\n', '')
    except CommandNotFound:
        return ''
    return ver


def project_root():
    try:
        root = sh.git('rev-parse', '--show-toplevel').stdout.replace('\n', '')
    except ErrorReturnCode:
        return ''
    return root


def describe_hash():
    try:
        tagver = sh.git(
            'describe', '--long', '--match=v*').stdout.replace('\n', '')
        vm = re.match(hash_matcher, tagver).groups()
        if len(vm) != 1:
            raise AttributeError
    except (ErrorReturnCode, AttributeError):
        return False
    return vm[0]


def count_tag_to_head(tag):
    try:
        c = sh.git(
            'rev-list', tag + "..HEAD", '--count').stdout.replace('\n', '')
        return int(c)
    except ErrorReturnCode:
        return False


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


def data_from_tag(tag):
    try:
        data = re.match(tag_matcher, tag).groups()
        if len(data) < 3:
            raise AttributeError
    except AttributeError:
        return None
    return data


def get_repo_info():
    # retrieve basic repository information
    desc_hash = describe_hash()
    if desc_hash is None or not desc_hash:
        print err("Error, couldn't describe current hash")
        sys.exit(1)

    hashlen = len(desc_hash)
    full_build_id = get_build_id()
    if not full_build_id or hashlen == 0:
        print err("Couldn't retrieve build id information")
        sys.exit(1)

    # sanity check
    if not full_build_id.startswith(desc_hash):
        print err("Hash problem detected: git-describe reports " + desc_hash +
                  ", but HEAD id is " + full_build_id)
        sys.exit(1)

    tag = last_tag()
    if not tag:
        print err("Couldn't retrieve the latest tag")
        sys.exit(1)

    data = data_from_tag(tag)
    if data is None:
        print "Couldn't retrieve version information from tag \"" + tag + "\""
        sys.exit(1)

    vmaj = int(data[0])
    vmin = int(data[1])
    vpatch = int(data[2])
    pr = data[3]
    vcount = count_tag_to_head(tag)

    return {'maj': vmaj, 'min': vmin, 'patch': vpatch, 'count': vcount,
            'build-id': full_build_id[:hashlen], 'full-build-id': full_build_id,
            'last-tag': tag, 'pr': pr}
