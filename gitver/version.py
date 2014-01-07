#!/usr/bin/env python2
# coding=utf-8


gitver_version = ''
gitver_buildid = ''
gitver_pypi = ''

try:
    import _version as v
    gitver_version = v.gitver_version
    gitver_buildid = v.gitver_buildid
    gitver_pypi = v.gitver_pypi
except ImportError:
    pass
