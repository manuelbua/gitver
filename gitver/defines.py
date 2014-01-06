#!/usr/bin/env python2
# coding=utf-8

"""
Project definitions
"""

import os
from gitver.git import project_root

PRJ_ROOT = project_root()

CFGDIRNAME = ".gitver"
CFGDIR = os.path.join(PRJ_ROOT, CFGDIRNAME)
CFGFILE = os.path.join(CFGDIR, "config")
GITIGNOREFILE = os.path.join(PRJ_ROOT, ".gitignore")
