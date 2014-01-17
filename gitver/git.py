#!/usr/bin/env python2
# coding=utf-8

"""
git support library
"""

import sys
import re
from gitver.termcolors import term

# check for the sh package
try:
    import sh
    from sh import ErrorReturnCode, CommandNotFound
except ImportError:
    term.err("A dependency is missing, please install the \"sh\" package and "
             "run gitver again.")
    sys.exit(1)

hash_matcher = r".*-g([a-fA-F0-9]+)"
tag_matcher = r"v{0,1}(?P<maj>\d+)\.(?P<min>\d+)\.(?P<patch>\d+)" \
              r"(?:\.(?P<revision>\d+))?[^-]*(?:-(?P<prmeta>[0-9A-Za-z-.]*))?"


def __git_raw(*args):
    """
    @return sh.RunningCommand
    Proxies the specified git command+args and returns it
    """
    return sh.git(args)


def __git(*args):
    """
    Proxies the specified git command+args and returns a cleaned up version
    of the stdout buffer.
    """
    return __git_raw(*args).stdout.replace('\n', '')


def git_version():
    try:
        ver = __git('--version')
    except (CommandNotFound, ErrorReturnCode):
        return ''
    return ver


def project_root():
    try:
        root = __git('rev-parse', '--show-toplevel')
    except ErrorReturnCode:
        return ''
    return root


def count_tag_to_head(tag):
    try:
        c = __git('rev-list', tag + "..HEAD", '--count')
        return int(c)
    except ErrorReturnCode:
        return False


def get_build_id():
    try:
        full_build_id = str(__git('rev-parse', 'HEAD'))
    except ErrorReturnCode:
        return False
    return full_build_id


def last_tag():
    try:
        tag = __git('describe', '--abbrev=0')
    except ErrorReturnCode:
        return False

    return tag


def data_from_tag(tag):
    try:
        data = re.match(tag_matcher, tag).groupdict()
        if len(data) < 3:
            raise AttributeError
    except AttributeError:
        return None
    return data


def min_hash_length():
    """
    Determines the minimum length of an hash string for this repository
    to uniquely describe a commit.
    gitver's minimum length is 7 characters, to avoid frequent hash string
    length variations in fast-growing projects.
    """
    try:
        out = __git_raw('rev-list', '--all', '--abbrev=0',
                        '--abbrev-commit').stdout
    except ErrorReturnCode:
        return 0

    min_accepted = 7

    # build a set of commit hash lengths
    commits = {
        len(commit) for commit in out.split('\n') if len(commit) >= min_accepted
    }

    if len(commits) > 0:
        # pick the max
        return max(commits)

    return min_accepted


def get_repo_info():
    """
    Retrieves raw repository information and returns it for further processing
    """
    hashlen = min_hash_length()
    if not hashlen:
        term.err("Couldn't compute the minimum hash string length")
        sys.exit(1)

    full_build_id = get_build_id()
    if not full_build_id:
        term.err("Couldn't retrieve build id information")
        sys.exit(1)

    tag = last_tag()
    if not tag:
        term.err("Couldn't retrieve the latest tag")
        sys.exit(1)

    data = data_from_tag(tag)
    if data is None:
        term.err("Couldn't retrieve version information from tag \"" + tag +
                 "\".\ngitver expects tags to be in the format "
                 "[v]X.Y.Z[.REVISION][-PRE-RELEASE-METADATA]")
        sys.exit(1)

    vcount = count_tag_to_head(tag)

    return {'maj': data['maj'],
            'min': data['min'],
            'patch': data['patch'],
            'rev': data['revision'],
            'pr': data['prmeta'],
            'count': vcount,
            'full-build-id': full_build_id,
            'build-id': full_build_id[:hashlen],
            'last-tag': tag
    }
