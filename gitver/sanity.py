#!/usr/bin/env python2
# coding=utf-8

"""
Implements reused sanity checks
"""

import os
import sys
from gitver.termcolors import err, warn, bold
from gitver.defines import PRJ_ROOT, CFGDIR, CFGDIRNAME, GITIGNOREFILE


def check_project_root():
    if len(PRJ_ROOT) == 0:
        print err("Couldn't determine your project's root directory, is this "
                  "a valid git repository?")
        sys.exit(1)


def check_config():
    # check config directory exists
    if not os.path.exists(CFGDIR):
        print "Please run " + bold("gitver init") + " first."
        sys.exit(1)


def check_gitignore(exit_on_error=True):
    # check .gitignore for .gitver inclusion
    try:
        gifile = os.path.join(GITIGNOREFILE)
        with open(gifile, 'r') as f:
            if CFGDIRNAME in f.read():
                return
    except IOError:
        pass

    print warn("Warning: it's highly recommended to EXCLUDE the gitver "
               "configuration from the repository!")
    print "Please include the following line in your .gitignore file:"
    print "    " + CFGDIRNAME

    if exit_on_error:
        sys.exit(1)
    else:
        print ""
