#!/usr/bin/env python2
# coding=utf-8

"""
Defines gitver commands
"""

import re
import os
import sys
from string import Template

from termcolors import term, bold
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


def parse_templates(templates, repo, next_custom):
    for t in templates.split(' '):
        tpath = template_path(t)
        if os.path.exists(tpath):
            with open(tpath, 'r') as fp:
                lines = fp.readlines()

            if len(lines) < 2:
                term.err("The template \"" + t + "\" is not valid, aborting.")
                return

            if not lines[0].startswith('#'):
                term.err("The template \"" + t + "\" doesn't define any valid "
                                                 "output, aborting.")
                return

            output = str(lines[0]).strip(' #\n')

            # resolve relative paths to the project's root
            if not os.path.isabs(output):
                output = os.path.join(PRJ_ROOT, output)

            outdir = os.path.dirname(output)

            if not os.path.exists(outdir):
                term.err("The template output directory \"" + outdir +
                         "\" doesn't exists.")

            term.prn("Processing template \"" + bold(t) + "\" for " + output +
                     "...")

            lines = lines[1:]
            xformed = Template("".join(lines))
            vstring = build_version_string(repo, False, next_custom)
            args = build_format_args(repo, next_custom)
            keywords = {
                'CURRENT_VERSION': vstring,
                'MAJOR': args['maj'],
                'MINOR': args['min'],
                'PATCH': args['patch'],
                'BUILD_ID': args['build_id'],
                'FULL_BUILD_ID': args['build_id_full'],
                'COMMIT_COUNT': args['commit_count'],
                'COMMIT_COUNT_STR':
                str(args['commit_count']) if args['commit_count'] > 0 else '',

                'COMMIT_COUNT_PREFIX': args['commit_count_prefix'],
                'META_PR': args['meta_pr'],
                'META_PR_PREFIX': args['meta_pr_prefix']
            }

            try:
                res = xformed.substitute(keywords)
            except KeyError as e:
                term.err("Unknown key \"" + e.message + "\" found, aborting.")
                sys.exit(1)

            try:
                fp = open(output, 'w')
                fp.write(res)
                fp.close()
            except IOError:
                term.err("Couldn't write file \"" + output + "\"")

            stat = os.stat(output)
            term.prn("Done, " + str(stat.st_size) + " bytes written.")
        else:
            term.err("Couldn't find the \"" + t + "\" template")


def user_numbers_from_string(user):
    try:
        data = re.match(user_version_matcher, user).groups()
        if len(data) != 3:
            raise AttributeError
    except AttributeError:
        return False
    return data


def build_format_args(repo_info, next_custom=None):
    in_next = repo_info['count'] > 0
    has_next_custom = not next_custom is None and len(next_custom) > 0

    vmaj = repo_info['maj']
    vmin = repo_info['min']
    vpatch = repo_info['patch']
    vcount = repo_info['count']
    vpr = repo_info['pr']
    vbuildid = repo_info['build-id']
    has_pr = vpr is not None
    if in_next and has_next_custom and not has_pr:
        u = user_numbers_from_string(next_custom)
        if not u:
            term.err("Invalid custom NEXT version numbers detected!")
            sys.exit(1)
        vmaj = u[0]
        vmin = u[1]
        vpatch = u[2]

    meta_pr = vpr if has_pr else \
        cfg['default_meta_pr_in_next'] if in_next and has_next_custom else \
        cfg['default_meta_pr_in_next_no_next'] if in_next else ''

    args = {
        'maj': vmaj,
        'min': vmin,
        'patch': vpatch,
        'meta_pr': meta_pr,
        'meta_pr_prefix': cfg['meta_pr_prefix'] if len(meta_pr) > 0 else '',
        'commit_count': vcount,
        'commit_count_prefix': cfg['commit_count_prefix'] if vcount > 0 else '',
        'build_id': vbuildid,
        'build_id_full': repo_info['full-build-id']
    }

    return args


def build_version_string(repo, promote=False, next_custom=None):
    in_next = repo['count'] > 0
    has_next_custom = not next_custom is None and len(next_custom) > 0

    if promote:
        if has_next_custom:
            # simulates next real version after proper tagging
            version = next_custom
            return version
        else:
            return ''

    fmt = cfg['format'] if not in_next else cfg['format_next']
    return fmt % build_format_args(repo, next_custom)


def cmd_version(args):
    v = ('v' + gitver_version) if gitver_version is not None else 'n/a'
    b = gitver_buildid if gitver_buildid is not None else 'n/a'
    term.prn("This is gitver " + bold(v))
    term.prn("Full build ID is " + bold(b))
    from gitver import __license__
    term.prn(__license__)


def cmd_init(args):
    i = 0

    if not os.path.exists(CFGDIR):
        i += 1
        os.makedirs(CFGDIR)
        term.prn("Created " + CFGDIR)

    if not os.path.exists(TPLDIR):
        i += 1
        os.makedirs(TPLDIR)
        term.prn("Created " + TPLDIR)

    if i > 0:
        term.prn("Done.")
    else:
        term.prn("Nothing to do.")


def cmd_current(args):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']
    has_next_custom = next_store.has(last_tag)
    next_custom = next_store.get(last_tag) if has_next_custom else None
    term.prn(build_version_string(repo_info, False, next_custom))


def cmd_info(args):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']

    has_next_custom = next_store.has(last_tag)
    next_custom = next_store.get(last_tag) if has_next_custom else None

    if has_next_custom:
        nvn = term.next(next_custom)
    else:
        nvn = "none, defaulting to " + \
              term.next("-" + cfg['default_meta_pr_in_next_no_next']) + \
              " suffix"

    term.prn("Most recent tag: " + term.tag(last_tag))

    if repo_info['pr'] is None and repo_info['count'] > 0:
        term.prn("Using NEXT defined as: " + nvn)
        term.prn("(Pre-release metadata: none)")
    elif repo_info['pr'] is not None:
        term.prn("(NEXT defined as: " + nvn + ")")
        term.prn("Using pre-release metadata: " +
                 term.tag(str(repo_info['pr'])))

    term.prn("Current build ID: " + term.tag(repo_info['full-build-id']))

    promoted = build_version_string(repo_info, True, next_custom)
    term.prn(
        "Current version: " +
        term.ver("v" +
                      build_version_string(repo_info, False, next_custom)) +
        (" => " + term.prom("v" + promoted) if len(promoted) > 0 else '')
    )


def cmd_list_templates(args):
    tpls = [f for f in os.listdir(TPLDIR) if os.path.isfile(template_path(f))]
    if len(tpls) > 0:
        term.prn("Available templates:")
        for t in tpls:
            term.prn("    " + bold(t) + " (" + template_path(t) + ")")
    else:
        term.prn("No templates available in " + TPLDIR)


def cmd_build_template(args):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']
    has_next_custom = next_store.has(last_tag)
    next_custom = next_store.get(last_tag) if has_next_custom else None
    parse_templates(args.templates, repo_info, next_custom)


def cmd_next(args):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()

    last_tag = repo_info['last-tag']

    vn = args.next_version_numbers
    user = user_numbers_from_string(vn)
    if not user:
        term.err("Please specify valid version numbers.\nThe expected "
                 "format is <MAJ>.<MIN>.<PATCH>, e.g. v0.0.1 or 0.0.1")
        sys.exit(1)

    custom = "%d.%d.%d" % (int(user[0]), int(user[1]), int(user[2]))
    next_store.set(last_tag, custom).save()
    term.prn("Set NEXT version string to " + term.next(custom) +
             " for the current tag " + term.tag(last_tag))


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
        term.prn("Cleaned up custom string version \"" + next_custom +
                 "\" for tag \"" + tag + "\"")
    else:
        term.prn("No custom string version found for tag \"" + tag + "\"")


def cmd_cleanall(args):
    if os.path.exists(NEXT_STORE_FILE):
        os.unlink(NEXT_STORE_FILE)
        term.prn("Custom strings removed.")
    else:
        term.prn("No NEXT custom strings found.")


def cmd_list_next(args):
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']
    has_next_custom = next_store.has(last_tag)
    if not next_store.empty():
        def print_item(k, v):
            term.prn("    %s => %s" % (term.tag(k), term.next(v)) +
                     (' (*)' if k == last_tag else ''))

        term.prn("Currently set NEXT custom strings (*=most recent and "
                 "reachable tag):")
        for tag, vstring in sorted(next_store.items()):
            print_item(tag, vstring)

        if not has_next_custom:
            print_item(last_tag, '<undefined>')

    else:
        term.prn("No NEXT custom strings set.")
