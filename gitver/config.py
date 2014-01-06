#!/usr/bin/env python2
# coding=utf-8

"""
The default per-repository configuration
"""

import json
from os.path import exists, dirname
from gitver.defines import CFGFILE

default_config = {
    'next_suffix': 'NEXT',
    'next_custom_suffix': 'SNAPSHOT'
}


def init_or_load_user_config():
    # try load user configuration
    try:
        with open(CFGFILE, 'r') as f:
            user = json.load(f)
    except (IOError, ValueError) as v:
        user = dict()

        # save to file as an example
        if not exists(CFGFILE):
            if exists(dirname(CFGFILE)):
                with open(CFGFILE, 'w') as f:
                    json.dump(default_config, f)

    # merge user with defaults
    return dict(default_config, **user)

cfg = init_or_load_user_config()
