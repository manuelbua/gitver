#!/usr/bin/env python2
# coding=utf-8

"""
Implements various sanity checks
"""

import os
import sys
from gitver.termcolors import term, bold
from gitver.defines import PRJ_ROOT, CFGDIR, CFGDIRNAME, GITIGNOREFILE


def check_project_root():
    # tries to determine the project's root directory
    if len(PRJ_ROOT) == 0:
        term.err("Couldn't determine your project's root directory, is this "
                 "a valid git repository?")
        sys.exit(1)


def check_config_dir():
    # checks if configuration directory exists
    if not os.path.exists(CFGDIR):
        term.err("Please run " + bold("gitver init") + " first.")
        sys.exit(1)


def check_gitignore():
    # checks .gitignore for .gitver inclusion
    try:
        gifile = os.path.join(GITIGNOREFILE)
        with open(gifile, 'r') as f:
            if CFGDIRNAME in f.read():
                return True
    except IOError:
        pass

    return False
