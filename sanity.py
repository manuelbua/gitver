#!/usr/bin/env python2
# coding=utf-8

"""
Implements reused sanity checks
"""

import os
import sys
from termcolors import err, warn, bold
from defines import GITDIR, CFGDIR, CFGDIRNAME


def check_gitdir():
    # check this is a git repo
    if not os.path.exists(GITDIR):
        print err("Please run this tool from within the parent of the .git "
                  "directory of your project.")
        sys.exit(1)


def check_config():
    # check config directory exists
    if not os.path.exists(CFGDIR):
        print "Please run " + bold("gitver init") + " first."
        sys.exit(1)


def check_gitignore():
    # check .gitignore for .gitver inclusion
    try:
        with open('.gitignore', 'r') as f:
            if CFGDIRNAME in f.read():
                return
    except IOError:
        pass

    print warn("Warning: it's highly recommended to EXCLUDE the gitver "
               "configuration from the repository!")
    print "Please include the following line in your .gitignore file:"
    print "    " + CFGDIRNAME
    sys.exit(1)
