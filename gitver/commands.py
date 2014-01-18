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
from defines import CFGDIR, PRJ_ROOT, CFGDIRNAME
from version import gitver_version, gitver_buildid


# file where to store NEXT strings <=> TAG user-defined mappings
NEXT_STORE_FILE = os.path.join(CFGDIR, ".next_store")
TPLDIR = os.path.join(CFGDIR, 'templates')

user_version_matcher = r"v{0,1}(?P<maj>\d+)\.(?P<min>\d+)\.(?P<patch>\d+)" \
                       r"(?:\.(?P<revision>\d+))?$"


#
# helpers
#

def template_path(name):
    """
    Constructs and returns the absolute path for the specified template file
    name.
    """
    return os.path.join(TPLDIR, name)


def parse_templates(cfg, templates, repo, next_custom, preview):
    """
    Parse one or more templates, substitute placeholder variables with
    real values and write the result to the file specified in the template.

    If preview is True, then the output will be written to the stdout while
    informative messages will be output to the stderr.
    """
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

            term.info("Processing template \"" + bold(t) + "\" for " + output +
                      "...")

            lines = lines[1:]
            xformed = Template("".join(lines))
            vstring = build_version_string(cfg, repo, False, next_custom)
            args = build_format_args(cfg, repo, next_custom)
            keywords = {
                'CURRENT_VERSION': vstring,
                'MAJOR': args['maj'],
                'MINOR': args['min'],
                'PATCH': args['patch'],
                'REV': args['rev'],
                'REV_PREFIX': args['rev_prefix'],
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

            if not preview:
                try:
                    fp = open(output, 'w')
                    fp.write(res)
                    fp.close()
                except IOError:
                    term.err("Couldn't write file \"" + output + "\"")
                    sys.exit(1)
            else:
                term.out(res)

            wrote_bytes = len(res) if preview else os.stat(output).st_size
            term.info("Done, " + str(wrote_bytes) + " bytes written.")
        else:
            term.err("Couldn't find the \"" + t + "\" template")
            sys.exit(1)


def parse_user_next_stable(user):
    """
    Parse the specified user-defined string containing the next stable version
    numbers and returns the discretized matches in a dictionary.
    """
    try:
        data = re.match(user_version_matcher, user).groupdict()
        if len(data) < 3:
            raise AttributeError
    except AttributeError:
        return False
    return data


def build_format_args(cfg, repo_info, next_custom=None):
    """
    Builds the formatting arguments by processing the specified repository
    information and returns them.

    If a tag defines pre-release metadata, this will have the precedence
    over any existing user-defined string.
    """
    in_next = repo_info['count'] > 0
    has_next_custom = next_custom is not None and len(next_custom) > 0

    vmaj = repo_info['maj']
    vmin = repo_info['min']
    vpatch = repo_info['patch']
    vrev = repo_info['rev']
    vcount = repo_info['count']
    vpr = repo_info['pr']
    vbuildid = repo_info['build-id']
    has_pr = vpr is not None
    has_rev = vrev is not None

    # pre-release metadata in a tag has precedence over user-specified
    # NEXT strings
    if in_next and has_next_custom and not has_pr:
        u = parse_user_next_stable(next_custom)
        if not u:
            term.err("Invalid custom NEXT version numbers detected!")
            sys.exit(1)
        vmaj = u['maj']
        vmin = u['min']
        vpatch = u['patch']
        vrev = u['revision']
        has_rev = vrev is not None

    meta_pr = vpr if has_pr else \
        cfg['default_meta_pr_in_next'] if in_next and has_next_custom else \
        cfg['default_meta_pr_in_next_no_next'] if in_next else ''

    args = {
        'maj': vmaj,
        'min': vmin,
        'patch': vpatch,
        'rev': vrev if has_rev else '',
        'rev_prefix': '.' if has_rev else '',
        'meta_pr': meta_pr,
        'meta_pr_prefix': cfg['meta_pr_prefix'] if len(meta_pr) > 0 else '',
        'commit_count': vcount,
        'commit_count_prefix': cfg['commit_count_prefix'] if vcount > 0 else '',
        'build_id': vbuildid,
        'build_id_full': repo_info['full-build-id']
    }

    return args


def build_version_string(cfg, repo, promote=False, next_custom=None):
    """
    Builds the final version string by processing the specified repository
    information, optionally handling version promotion.

    Version promotion will just return the user-specified next version string,
    if any is present, else an empty string will be returned.
    """
    in_next = repo['count'] > 0
    has_next_custom = next_custom is not None and len(next_custom) > 0

    if promote:
        if has_next_custom:
            # simulates next real version after proper tagging
            version = next_custom
            return version
        else:
            return ''

    fmt = cfg['format'] if not in_next else cfg['format_next']
    return fmt % build_format_args(cfg, repo, next_custom)


#
# commands
#

def cmd_version(cfg, args):
    """
    Generates gitver's version string and license information and prints it
    to the stdout.
    """
    v = ('v' + gitver_version) if gitver_version is not None else 'n/a'
    b = gitver_buildid if gitver_buildid is not None else 'n/a'
    term.out("This is gitver " + bold(v))
    term.out("Full build ID is " + bold(b))
    from gitver import __license__
    term.out(__license__)


def cmd_init(cfg, args):
    """
    Initializes the current repository by creating the gitver's configuration
    directory and creating the default configuration file, if none is present.

    Multiple executions of this command will regenerate the default
    configuration file whenever it's not found.
    """
    from config import create_default_configuration_file
    i = 0

    if not os.path.exists(CFGDIR):
        i += 1
        os.makedirs(CFGDIR)

    if not os.path.exists(TPLDIR):
        i += 1
        os.makedirs(TPLDIR)

    # try create the default configuration file
    wrote_cfg = create_default_configuration_file()

    if wrote_cfg:
        term.out("gitver has been initialized and configured.")
    else:
        term.warn("gitver couldn't create the default configuration file, "
                  "does it already exist?")


def cmd_current(cfg, args):
    """
    Generates the current version string, depending on the state of the
    repository and prints it to the stdout.
    """
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']
    has_next_custom = next_store.has(last_tag)
    next_custom = next_store.get(last_tag) if has_next_custom else None
    term.out(build_version_string(cfg, repo_info, False, next_custom))


def cmd_info(cfg, args):
    """
    Generates version string and repository information and prints it to the
    stdout.
    """
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

    term.out("Most recent tag: " + term.tag(last_tag))

    if repo_info['pr'] is None and repo_info['count'] > 0:
        term.out("Using NEXT defined as: " + nvn)
        term.out("(Pre-release metadata: none)")
    elif repo_info['pr'] is not None:
        term.out("(NEXT defined as: " + nvn + ")")
        term.out("Using pre-release metadata: " +
                 term.tag(str(repo_info['pr'])))

    term.out("Current build ID: " + term.tag(repo_info['full-build-id']))

    promoted = build_version_string(cfg, repo_info, True, next_custom)
    term.out(
        "Current version: " +
        term.ver("v" + build_version_string(
            cfg, repo_info, False, next_custom)) +
        (" => " + term.prom("v" + promoted) if len(promoted) > 0 else '')
    )


def cmd_list_templates(cfg, args):
    """
    Generates a list of available templates by inspecting the gitver's template
    directory and prints it to the stdout.
    """
    tpls = [f for f in os.listdir(TPLDIR) if os.path.isfile(template_path(f))]
    if len(tpls) > 0:
        term.out("Available templates:")
        for t in tpls:
            term.out("    " + bold(t) + " (" + template_path(t) + ")")
    else:
        term.out("No templates available in " + TPLDIR)


def __cmd_build_template(cfg, args, preview=False):
    """
    Internal-only function used for avoiding code duplication between
    template-operating functions.

    See cmd_build_template and cmd_preview_template for the full docs.
    """
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']
    has_next_custom = next_store.has(last_tag)
    next_custom = next_store.get(last_tag) if has_next_custom else None
    parse_templates(cfg, args.templates, repo_info, next_custom, preview)


def cmd_build_template(cfg, args):
    """
    Performs placeholder variables substitution on the templates specified by
    the @param args parameter and write the result to each respective output
    file specified by the template itself.
    """
    __cmd_build_template(cfg, args)


def cmd_preview_template(cfg, args):
    """
    Performs placeholder variables substitution on the templates specified by
    the @param args parameter and prints the result to the stdout.
    """
    __cmd_build_template(cfg, args, True)


def cmd_next(cfg, args):
    """
    Sets and defines the next stable version string for the most recent and
    reachable tag.

    The string should be supplied in the format "maj.min.patch[.revision]",
    where angular brackets denotes an optional value.

    All values are expected to be decimal numbers without leading zeros.
    """
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()

    last_tag = repo_info['last-tag']

    vn = args.next_version_numbers
    user = parse_user_next_stable(vn)
    if not user:
        term.err("Please specify valid version numbers.\nThe expected "
                 "format is <MAJ>.<MIN>.<PATCH>[.<REVISION>], e.g. v0.0.1, "
                 "0.0.1 or 0.0.2.1")
        sys.exit(1)

    custom = "%d.%d.%d" % (int(user['maj']), int(user['min']), int(user['patch']))

    if user['revision'] is not None:
        custom += ".%d" % (int(user['revision']))

    next_store.set(last_tag, custom).save()
    term.out("Set NEXT version string to " + term.next(custom) +
             " for the current tag " + term.tag(last_tag))


def cmd_clean(cfg, args):
    """
    Removes the user-defined next stable version for the most recent and
    reachable tag or for the tag specified by the @param args parameter.
    """
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
        term.out("Cleaned up custom string version \"" + next_custom +
                 "\" for tag \"" + tag + "\"")
    else:
        term.out("No custom string version found for tag \"" + tag + "\"")


def cmd_cleanall(cfg, args):
    """
    Removes ALL user-defined next stable versions.
    """
    if os.path.exists(NEXT_STORE_FILE):
        os.unlink(NEXT_STORE_FILE)
        term.out("All previously set custom strings have been removed.")
    else:
        term.out("No NEXT custom strings found.")


def cmd_list_next(cfg, args):
    """
    Generates a list of all user-defined next stable versions and prints them
    to the stdout.
    """
    next_store = KVStore(NEXT_STORE_FILE)
    repo_info = get_repo_info()
    last_tag = repo_info['last-tag']
    has_next_custom = next_store.has(last_tag)
    if not next_store.empty():
        def print_item(k, v):
            term.out("    %s => %s" % (term.tag(k), term.next(v)) +
                     (' (*)' if k == last_tag else ''))

        term.out("Currently set NEXT custom strings (*=most recent and "
                 "reachable tag):")
        for tag, vstring in sorted(next_store.items()):
            print_item(tag, vstring)

        if not has_next_custom:
            print_item(last_tag, '<undefined>')

    else:
        term.out("No NEXT custom strings set.")


def cmd_check_gitignore(cfg, args):
    """
    Provides a way to ensure that at least one line in the .gitignore file for
    the current repository defines the '.gitver' directory in some way.

    This means that even a definition such as "!.gitver" will pass the check,
    but this imply some reasoning has been made before declaring something like
    this.
    """
    if check_gitignore():
        term.out("Your .gitignore file looks fine.")
    else:
        term.out("Your .gitignore file doesn't define any rule for the " +
                 CFGDIRNAME + "\nconfiguration directory: it's recommended to "
                 "exclude it from\nthe repository, unless you know what you "
                 "are doing. If you are not\nsure, add this line to your "
                 ".gitignore file:\n\n    " + CFGDIRNAME + "\n")
