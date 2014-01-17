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
from termcolors import term, bold

default_config_text = """{
    # automatically generated configuration file
    #
    # These defaults implement Semantic Versioning as described in the latest
    # available documentation at http://semver.org/spec/v2.0.0.html

    # by default, terminal output is NOT colorized for compatibility with older
    # terminal emulators: you may enable this if you like a more modern look
    "use_terminal_colors": false,

    # prevent gitver from storing any information in its configuration directory
    # if the .gitignore file doesn't exclude it from the repository
    "safe_mode": true,

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
    #     maj, min, patch, rev, rev_prefix, meta_pr_prefix, meta_pr,
    #     commit_count_prefix, commit_count, build_id, build_id_full
    #
    # Note that prefixes will be empty strings if their valued counterpart
    # doesn't have a meaningful value (i.e., 0 for commit count, no meta
    # pre-release, ..)

    # format string used to build the current version string when the
    # commit count is 0
    "format": "%(maj)s.%(min)s.%(patch)s%(rev_prefix)s%(rev)s%(meta_pr_prefix)s%(meta_pr)s",

    # format string used to build the current version string when the
    # commit count is > 0
    "format_next": "%(maj)s.%(min)s.%(patch)s%(rev_prefix)s%(rev)s%(meta_pr_prefix)s%(meta_pr)s%(commit_count_prefix)s%(commit_count)s+%(build_id)s"
}"""


def remove_comments(text):
    """
    Removes line comments denoted by sub-strings starting with a '#'
    character from the specified string, construct a new text and returns it.
    """
    data = string.split(text, '\n')
    ret = ''
    for line in data:
        if not line.strip().startswith('#'):
            ret += line
    return ret


default_config = json.loads(remove_comments(default_config_text))


def create_default_configuration_file():
    """
    Creates a default configuration file from the default gitver's
    configuration text string in the predefined gitver's configuration
    directory.
    """
    if not exists(CFGFILE):
        if exists(dirname(CFGFILE)):
            with open(CFGFILE, 'w') as f:
                f.writelines(default_config_text)
                return True
    return False


def load_user_config():
    """
    Returns the gitver's configuration: tries to read the stored configuration
    file and merges it with the default one, ensuring a valid configuration is
    always returned.
    """
    try:

        with open(CFGFILE, 'r') as f:
            data = ''
            for line in f:
                l = line.strip()
                if not l.startswith('#'):
                    data += l
            user = json.loads(data)

    except IOError:
        user = dict()

    except (ValueError, KeyError) as v:
        term.err("An error occured parsing the configuration file \"" +
                 CFGFILE + "\": " + v.message +
                 "\nPlease check its syntax or rename it and generate the "
                 "default one with the " + bold("gitver init") + " command.")
        sys.exit(1)

    # merge user with defaults
    return dict(default_config, **user)
