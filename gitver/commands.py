#!/usr/bin/env python2
# coding=utf-8

"""
Defines gitver commands
"""

import re
import os
import sys
from string import Template

from termcolors import *
from git import get_repo_info
from gitver.storage import KVStore
from sanity import check_gitignore
from defines import CFGDIR, PRJ_ROOT
from config import cfg
from version import gitver_version, gitver_buildid

# file where to store NEXT strings <=> TAG user-defined mappings
NEXT_STORE_FILE = os.path.join(CFGDIR, ".next_store")
TPLDIR = os.path.join(CFGDIR, 'templates')

user_version_matcher = r"v{0,1}(\d+)\.(\d+)\.(\d+)$"


def template_path(name):
    return os.path.join(TPLDIR, name)


def parse_templates(templates, repo, next_custom, promote):
    has_next_custom = not next_custom is None and len(next_custom) > 0
    if promote and not has_next_custom:
        print err("No NEXT version to promote to, aborting.")
        sys.exit(1)

    for t in templates.split(' '):
        tpath = template_path(t)
        if os.path.exists(tpath):
            with open(tpath, 'r') as fp:
                lines = fp.readlines()

            if len(lines) < 2:
                print err("The template \"" + t + "\" is not valid")
                return

            output = str(lines[0]).strip(' #\n')

            # resolve relative paths to the project's root
            if not os.path.isabs(output):
                output = os.path.join(PRJ_ROOT, output)
            print output

            outdir = os.path.dirname(output)

            if not os.path.exists(outdir):
                print err("The template output directory \"" + outdir +
                          "\" doesn't exists.")

            print "Processing template \"" + bold(t) + "\" for " + output + \
                  "..."

            lines = lines[1:]
            xformed = Template("".join(lines))
            vstring = build_version_string(repo, promote, next_custom)

            comm_count = repo['count'] if not promote else 0
            in_next = comm_count > 0
            suffix = ''
            sep = ''

            if in_next:
                sep = '-'
                if has_next_custom:
                    suffix = cfg['next_custom_suffix']
                else:
                    suffix = cfg['next_suffix']

            # this should NEVER fail
            has_user_string = (promote or in_next) and not next_custom is None
            if has_user_string:
                user = user_numbers_from_string(next_custom)
                if not user:
                    print err("Invalid custom NEXT version numbers detected, "
                              "this should NEVER happen at this point!")
                    sys.exit(1)

            keywords = {
                'CURRENT_VERSION': vstring,
                'BUILD_ID': repo['build-id'],
                'FULL_BUILD_ID': repo['full-build-id'],
                'MAJOR': repo['maj'] if not has_user_string else int(user[0]),
                'MINOR': repo['min'] if not has_user_string else int(user[1]),
                'PATCH': repo['patch'] if not has_user_string else int(user[2]),
                'COMMIT_COUNT': comm_count,
                'SUFFIX': suffix,
                'SEP': sep,
                'COMMIT_COUNT_STR': str(comm_count) if comm_count > 0 else ''
            }

            try:
                res = xformed.substitute(keywords)
            except KeyError as e:
                print "Unknown key \"" + e.message + "\" found, aborting."
                sys.exit(1)

            try:
                fp = open(output, 'w')
                fp.write(res)
                fp.close()
            except IOError:
                print err("Couldn't write file \"" + output + "\"")

            stat = os.stat(output)
            print "Done, " + str(stat.st_size) + " bytes written."
        else:
            print err("Couldn't find the \"" + t + "\" template")


def user_numbers_from_string(user):
    try:
        data = re.match(user_version_matcher, user).groups()
        if len(data) != 3:
            raise AttributeError
    except AttributeError:
        return False
    return data


def build_version_string(repo, promote=False, next_custom=None):
    in_next = repo['count'] > 0
    has_next_custom = not next_custom is None and len(next_custom) > 0
    if promote:
        if has_next_custom:
            # simulates next real version after proper tagging
            version = next_custom
            version += "/" + repo['build-id']
            return version
        else:
            return ''

    if in_next and has_next_custom:
        version = next_custom
        version += "-" + cfg['next_custom_suffix']
    else:
        version = "%d.%d.%d" % (repo['maj'], repo['min'], repo['patch'])
        if in_next:
            version += "-" + cfg['next_suffix']

    if in_next:
        version += "-" + str(repo['count'])

    version += "/" + repo['build-id']

    return version


def cmd_version(args):
    v = ('v' + gitver_version) if gitver_version is not None else 'n/a'
    b = gitver_buildid if gitver_buildid is not None else 'n/a'
    print "This is gitver " + bold(v)
    print "Full build ID is " + bold(b)


def cmd_init(args):
    i = 0

    if not os.path.exists(CFGDIR):
        i += 1
        os.makedirs(CFGDIR)
        print "Created " + CFGDIR

    if not os.path.exists(TPLDIR):
        i += 1
        os.makedirs(TPLDIR)
        print "Created " + TPLDIR

    check_gitignore()

    if i > 0:
        print "Done."
    else:
        print "Nothing to do."


def cmd_info(args):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']

    has_next_custom = next_store.has(last_tag)
    next_custom = next_store.get(last_tag) if has_next_custom else None

    if has_next_custom:
        nvn = color_next(next_custom)
    else:
        nvn = "none defined, using " + color_next("-" + cfg['next_suffix']) + \
              " suffix"

    print "Most recent tag: " + color_tag(last_tag)
    print "NEXT defined as: " + nvn
    print "Current build ID: " + color_tag(repo_info['full-build-id'])
    promoted = build_version_string(repo_info, True, next_custom)
    print "Current version: " + \
          color_version(
              "v" + build_version_string(repo_info, False, next_custom) +
              (" => v" + promoted if len(promoted) > 0 else '')
          )


def cmd_list_templates(args):
    tpls = [f for f in os.listdir(TPLDIR) if os.path.isfile(template_path(f))]
    if len(tpls) > 0:
        print "Available templates:"
        for t in tpls:
            print "    " + bold(t) + " (" + template_path(t) + ")"
    else:
        print "No templates available in " + TPLDIR


def _cmd_build_template(args, promote=False):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']
    has_next_custom = next_store.has(last_tag)
    next_custom = next_store.get(last_tag) if has_next_custom else None
    parse_templates(args.templates, repo_info, next_custom, promote)


def cmd_build_template(args):
    _cmd_build_template(args, False)


def cmd_build_template_prom(args):
    _cmd_build_template(args, True)


def cmd_next(args):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()

    last_tag = repo_info['last-tag']

    vn = args.next_version_numbers
    user = user_numbers_from_string(vn)
    if not user:
        print err("Please specify valid version numbers.\nThe expected "
                  "format is <MAJ>.<MIN>.<PATCH>, e.g. v0.0.1 or 0.0.1")
        sys.exit(1)

    custom = "%d.%d.%d" % (int(user[0]), int(user[1]), int(user[2]))
    next_store.set(last_tag, custom).save()
    print "Set NEXT version string to " + color_next(custom) + \
          " for the current tag " + color_tag(last_tag)


def cmd_clean(args):
    next_store = KVStore(NEXT_STORE_FILE)
    if len(args.tag) > 0:
        tag = args.tag
    else:
        repo_info = get_repo_info()
        tag = repo_info['last-tag']

    has_custom = next_store.has(tag)
    next_custom = next_store.get(tag) if has_custom else None

    if has_custom:
        next_store.rm(tag).save()
        print "Cleaned up custom string version \"" + next_custom + \
              "\" for tag \"" + tag + "\""
    else:
        print "No custom string version found for tag \"" + tag + "\""


def cmd_cleanall(args):
    if os.path.exists(NEXT_STORE_FILE):
        os.unlink(NEXT_STORE_FILE)
        print "Custom strings removed."
    else:
        print "No NEXT custom strings found."


def cmd_list_next(args):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']
    has_next_custom = next_store.has(last_tag)
    if not next_store.empty():
        def print_item(k, v):
            print "    %s => %s" % (color_tag(k), color_next(v)) +\
                  (' (*)' if k == last_tag else '')

        print "Currently set NEXT custom strings (*=most recent " \
              "and reachable tag):"
        for tag, vstring in sorted(next_store.items()):
            print_item(tag, vstring)

        if not has_next_custom:
            print_item(last_tag, '<undefined>')

    else:
        print "No NEXT custom strings set."
