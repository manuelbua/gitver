#!/usr/bin/env python2
# coding=utf-8

"""
The default per-repository configuration
"""

import sys
import json
import string
from os.path import exists, dirname
from gitver.defines import CFGFILE
from termcolors import term

default_config_text = """{
    # automatically generated configuration file
    #
    # These defaults implements Semantic Versioning as described in the latest
    # available documentation at http://semver.org/spec/v2.0.0.html

    # by default, terminal output is colorized: you may disable this if you
    # experience problems
    "use_terminal_colors": false,

    # default pre-release metadata when commit count > 0 AND
    # no NEXT has been defined
    "default_meta_pr_in_next_no_next": "NEXT",

    # default pre-release metadata when commit count > 0
    "default_meta_pr_in_next": "SNAPSHOT",

    # default pre-release metadata prefix
    "meta_pr_prefix": "-",

    # default commit count prefix
    "commit_count_prefix": ".",

    # Python-based format string variable names are:
    #     maj, min, patch, meta_pr_prefix, meta_pr, commit_count_prefix,
    #     commit_count, build_id, build_id_full
    # Note that prefixes will be empty strings if their valued counterpart doesn't
    # have a meaningful value (i.e., 0 for commit count, no meta pre-release, ..)

    # format string used to build the current version string when the
    # commit count is 0
    "format": "%(maj)s.%(min)s.%(patch)s%(meta_pr_prefix)s%(meta_pr)s",

    # format string used to build the current version string when the
    # commit count is > 0
    "format_next": "%(maj)s.%(min)s.%(patch)s%(meta_pr_prefix)s%(meta_pr)s%(commit_count_prefix)s%(commit_count)s+%(build_id)s"
}"""


def remove_comments(text):
    data = string.split(text, '\n')
    ret = ''
    for line in data:
        if not line.strip().startswith('#'):
            ret += line
    return ret


default_config = json.loads(remove_comments(default_config_text))


def init_or_load_user_config():
    # try load user configuration
    try:

        with open(CFGFILE, 'r') as f:
            data = ''
            for line in f:
                l = line.strip()
                if not l.startswith('#'):
                    data += l
            user = json.loads(data)

            # check for old configuration file format
            if len(user) <= 2:
                term.warn("Your configuration file \"" + CFGFILE +
                          "\" is a deprecated version.\nPlease rename or "
                          "remove it, gitver will then create a new one for "
                          "you.")

    except IOError:
        user = dict()

        # save to file as an example
        if not exists(CFGFILE):
            if exists(dirname(CFGFILE)):
                with open(CFGFILE, 'w') as f:
                    f.writelines(default_config_text)
                    term.prn("(wrote default configuration file \"" + CFGFILE +
                             "\")")

    except ValueError as v:
        term.prn("An error occured parsing the configuration file at \"" +
                 CFGFILE + "\": " + v.message)
        term.prn("You could rename or delete it, gitver will then create a "
                 "new one for you.")
        sys.exit(1)

    # merge user with defaults
    return dict(default_config, **user)

cfg = init_or_load_user_config()
