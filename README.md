[![PyPi version](https://pypip.in/v/gitver/badge.png)](https://crate.io/packages/gitver/)
[![PyPi downloads](https://pypip.in/d/gitver/badge.png)](https://crate.io/packages/gitver/)

## What is it?
A very simple, lightweight, tag-based version string manager for git, written in Python.

It generates version strings by using Python-based formatting rules coupled with repository information, augmented by user-defined data.

Makes very easy to adopt versioning schemes such as [Semantic Versioning](https://semver.org) and keeps version information automagically updated.

Sample output (this repository):

    Most recent tag: v0.3.0-RC
    Using pre-release metadata: RC
    Current build ID: 977fbbc7043691ed519cb26ab62772ef8fa8a582
    Current version: v0.3.0-RC

## Helps in version string management

Coupled with [git hooks](http://git-scm.com/book/en/Customizing-Git-Git-Hooks), *gitver* version blob templates helps to keep your own project updated with its version information, performing simple template-based substitution automatically at *post-commit* time, for example.


## Why?

I'm working on a project that requires precise version string tracking and synchronization between a server and its different clients, so an automatic mechanism is needed.

Furthermore, i want the version string and/or other useful information to be **embedded** in the application code automatically, "compiled-in" so to speak, without me having to remember to do it manually each time.

## Workflow

Your workflow shouldn't change much from what you are used to, but before using it, please ensure your repository's tags are **not** already being used for some other purpose, *gitver* expects them in the format `vX.Y.Z` or `vX.Y.Z-PRE-RELEASE-METADATA`

The following is a workflow exemplification of using *gitver* to manage version strings for your project, given it has already been setup:

- you are working on your repository, now you are ready to promote the current version to the next release
- create a release tag, `git tag -a v0.0.2 -m 'Bump version'`
- defines your NEXT version, the one you are going to work *towards* to by running `gitver next 0.0.3`
- run `gitver` and check everything is fine
- **OPTIONAL** update your project's version information by running `gitver update <template name>`, then rebuild the project to reflect version changes
- any other manual house-keeping in-between releases can be performed now
- now you are working towards the NEXT release, repeat when release time has came again


## Notes on the example output in this document

As of `v0.3.0-RC1`, the default version string format has changed, adopting the [Semantic Versioning](https://semver.org) scheme: example output such as `v0.0.0/e2c8ce21` will be different, but the workflow itself hasn't changed, so you should be able to follow this document without problems.

*I'll update the examples' output as soon as i've the time to do it, sorry!*


## How does it work?

By reading your last reachable **annotated** tag, it will generate human-readable version strings, distinguishing automatically between *stable* and *development* builds, depending on the number of commits from that last tag (the *commit count*).

As an example, let's assume the following history:

    * 81dfbe1  (master) (Sun Jan 5 14:25:32 2014) some more
    * 1200eec  (Sun Jan 5 14:24:59 2014) changed stuff
    * 1d36d68  (Sun Jan 5 14:24:42 2014) another change
    * e2c8ce2  (HEAD, tag: v0.0.0) (Sun Jan 5 14:02:36 2014) test

In this case the commit count is `0` (HEAD is at `v0.0.0`), so a version string for a *stable* build will be generated:

    v0.0.0/e2c8ce21

Note how stable builds do not have any suffix and the commit count of `0` is just discarded.
By moving HEAD to `master`, instead, will produce a slightly different version string, let's see that:

    * 81dfbe1  (HEAD, master) (Sun Jan 5 14:25:32 2014) some more
    * 1200eec  (Sun Jan 5 14:24:59 2014) changed stuff
    * 1d36d68  (Sun Jan 5 14:24:42 2014) another change
    * e2c8ce2  (tag: v0.0.0) (Sun Jan 5 14:02:36 2014) test

Now the commit count is `3`, this indicates that you are working toward the NEXT release, the NEXT version numbers haven't been defined yet, so the newly generated version string will now be:

    v0.0.0-NEXT-3/81dfbe12

This is the default form of describing a NEXT release, that is, when a NEXT version has not yet been defined but some work has been done **past** the last tagged release: it's quite similar to the one produced by `git describe`, in fact the information are the very same, only the -NEXT suffix has been added in-between.

But we can do more than this: *gitver* gives the option to define the NEXT version numbers for the latest tag, so let's define it to be `0.0.1`:

    gitver next 0.0.1
    Set NEXT version string to 0.0.1 for the current tag v0.0.0

Now that it has been set, the very same point in development can then be described more intelligently:

    v0.0.1-SNAPSHOT-3/81dfbe12

Got it? You basically defined what the next tag name *will* be, and the correct version string is generated for you.

Unhappy of what you have choosen for the next version numbers? Want to bump a bit more? Then just set the NEXT version numbers to something else:

    gitver next 1.0.0
    Set NEXT version string to 1.0.0 for the current tag v0.0.0

The version string will now be:

    v1.0.0-SNAPSHOT-3/81dfbe12


## Config file

*gitver* uses a per-repository, JSON-based configuration file.

The default configuration file gets created automatically in `.gitver/config` and it contains the following, tweakable settings:

    {
        # automatically generated configuration file
        #
        # These defaults implements Semantic Versioning as described in the latest
        # available documentation at http://semver.org/spec/v2.0.0.html

        # default pre-release metadata when commit count > 0 AND
        # no NEXT has been defined
        "default_meta_pr_in_next_no_next": "NEXT",

        # default pre-release metadata when commit count > 0
        "default_meta_pr_in_next": "SNAPSHOT",

        # default pre-release metadata prefix
        "meta_pr_prefix": "-",

        # default commit count prefix
        "commit_count_prefix": "-",

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
    }

## Basic usage 

    $ gitver --help
    usage: gitver [-h] [--ignore-gitignore]
                  
                  {version,init,info,current,list-templates,list-next,update,next,clean,cleanall}
                  ...

    optional arguments:
      -h, --help            show this help message and exit
      --ignore-gitignore    Ignore the .gitignore warning and continue running as
                            normal (specify this flag before any other command, at
                            YOUR own risk)

    Valid commands:
      {version,init,info,current,list-templates,list-next,update,next,clean,cleanall}
        version             Show gitver version
        init                Create gitver's configuration directory
        info                Print full version information and tag-based metadata
                            for this repository [default]
        current             Print the current version information only, without
                            any formatting applied.
        list-templates      Enumerates available templates
        list-next           Enumerates NEXT custom strings
        update              Perform simple keyword substitution on the specified
                            template file(s) and place it to the path described by
                            the first line in the template. This is usually
                            performed *AFTER* a release has been tagged already.
        next                Sets the NEXT version numbers for the currently
                            reachable last tag.
        clean               Resets the NEXT custom string for the currently active
                            tag, or the specified tag, to a clean state.
        cleanall            Resets all the NEXT custom strings for thisrepository.


The tool expects the tags in your repository to get used to describe version information in the format `vX.Y.Z` or `vX.Y.Z-PRE-RELEASE-METADATA`, so you should take that into account and use them to properly mark a release version in your repository.

If no tags in this format are found *gitver* will not run.

So, let's create a brand new repository at `/tmp/test` to test this tool on: we are going to look at *gitver* features step-by-step.

    cd /tmp && mkdir test && cd test && git init

Now populate it with some activity:

    echo "some data" > some && git add some && git commit -m 'initial commit' && echo "more data" > more && echo "another one" > another && git add more && git commit -m 'one more' && git add another && git commit -m 'even more'

Your repository should now look like this:

    * 9a06012  (HEAD, master) (Sun Jan 5 15:47:07 2014) even more (Manuel Bua)
    * 594b422  (Sun Jan 5 15:47:07 2014) one more (Manuel Bua)
    * 23fdbb5  (Sun Jan 5 15:47:07 2014) initial commit (Manuel Bua)

Let's initialize *gitver* at this point:

    $ gitver init
    Created .gitver/
    Created .gitver/templates
    Warning: it's highly recommended to EXCLUDE the gitver configuration from the repository!
    Please include the following line in your .gitignore file:
        .gitver

It's recommended to **exclude** gitver's configuration directory from the repository, in fact gitver will not run until the `.gitignore` file includes the `.gitver` directory (you can specify the `--ignore-gitignore` flag if you really want to): this is to prevent your own per-tag configuration to get lost whenever you checkout old revisions and you don't want that to happen, so let's exclude it:

    echo ".gitver" >> .gitignore

Now that this has been done, run *gitver*:

    $ gitver
    Error, this repository is required to define tags in the format vX.Y.Z

Right, we have no tags at this point, so let's create `v0.0.0` at the first commit with this command (replace the commit hash with your own where needed):

    git tag -a v0.0.0 -m 'Initial version' 23fdbb5

This is how your repository should look like:

    * 9a06012  (HEAD, master) (Sun Jan 5 15:47:07 2014) even more (Manuel Bua)
    * 594b422  (Sun Jan 5 15:47:07 2014) one more (Manuel Bua)
    * 23fdbb5  (tag: v0.0.0) (Sun Jan 5 15:47:07 2014) initial commit (Manuel Bua)

Now *gitver* output should be somewhat more informative:

    $ gitver
    Latest tag: v0.0.0
    NEXT: none defined, using -NEXT suffix
    Current build ID: 9a06012b7a6981e1cf9aaea4d393d2567a3ddfb9
    Current version: v0.0.0-NEXT-2/9a06012b

Time to decide what the NEXT version numbers will be, so let's set this and run *gitver* again:

    $ gitver next 0.0.1
    Set NEXT version string to 0.0.1 for the current tag v0.0.0

    $ gitver
    Latest tag: v0.0.0
    NEXT: 0.0.1
    Current build ID: 9a06012b7a6981e1cf9aaea4d393d2567a3ddfb9
    Current version: v0.0.1-SNAPSHOT-2/9a06012b

Notice how the build id stays the same but the version string changed: in fact both strings are describing the same thing, they are equivalent, but given the same intentions, i find the latter to be much more clear.

Let's add that `.gitignore` file we didn't add before and declare the version stable, all we have to do is to add a tag when ready:

    $ git add .gitignore && git commit -m 'Add .gitignore file'
    $ git tag -a 'v0.0.1' -m 'Bump version'
    $ gitver
    Latest tag: v0.0.1
    NEXT: none defined, using -NEXT suffix
    Current build ID: 7837a7cb69fb43f7acc54bb795b925538ee6cf5e
    Current version: v0.0.1/7837a7cb

The repository should now look like the following:

    * 7837a7c  (HEAD, tag: v0.0.1, master) (Sun Jan 5 16:07:36 2014) Add .gitignore file (Manuel Bua)
    * 9a06012  (Sun Jan 5 15:47:07 2014) even more (Manuel Bua)
    * 594b422  (Sun Jan 5 15:47:07 2014) one more (Manuel Bua)
    * 23fdbb5  (tag: v0.0.0) (Sun Jan 5 15:47:07 2014) initial commit (Manuel Bua)


Say now you need to perform a rebuild of an old revision for whatever reason, let's get back to an old state before `v0.0.1` release:

    $ git checkout v0.0.1~2

This is the repository now:

    * 7837a7c  (tag: v0.0.1, master) (Sun Jan 5 16:42:17 2014) Add .gitignore file (Manuel Bua)
    * 9a06012  (Sun Jan 5 16:39:59 2014) even more (Manuel Bua)
    * 594b422  (HEAD) (Sun Jan 5 16:39:59 2014) one more (Manuel Bua)
    * 23fdbb5  (tag: v0.0.0) (Sun Jan 5 16:39:59 2014) initial commit (Manuel Bua)

At this point, running *gitver* should generate the same `.gitignore` warning message as before: that is, recall that we didn't include `.gitver` configuration directory in the `.gitignore` file from the start, we did it only at a later time:

    $ gitver
    Warning: it's highly recommended to EXCLUDE the gitver configuration from the repository!
    Please include the following line in your .gitignore file:
        .gitver

    Latest tag: v0.0.0
    NEXT: 0.0.1
    Current build ID: 594b422bc1521aa1e242b63db672f3699ba70fe7
    Current version: v0.0.1-SNAPSHOT-1/594b422b

Note that this will not prevent operations such as `gitver info` to continue, but acting on the *gitver* storage via `gitver next` will be disabled, until you take action to exclude its directory from the repository.

Actually, you *can* force operations to continue (`--ignore-gitignore`), even if not recommended, but you must know what you are doing: *gitver* itself store your preferences in its .gitver directory and, whenever a checkout is performed, this data would change too, and that's not what you want.


## Template-based version information blobs

One of the main reasons for this script to exists is to be able to also automatically update the project own's version information *blob* (e.g. `VersionInfo.java`, `version.py`, ...) or some other external file with the project's version information.

If you plan to compile template often very often, then you may want to exclude them from the repository, with a `.gitignore` directive.


## Template format

The only **required** bit of information *gitver* needs is where the output of the template should be placed, so the first line shall only contain the path to the output file in a Bash-style comment (spaces are trimmed):

    # /path/to/project/file.extension

The rest of the file is obviously up to you, an example is available at the "Template example" section.


*Why is the format starting with a Bash-style comment, you say?* The initial version of *gitver* was a Bash script, so it was a natural choice to adopt that: i then realized i didn't like how things were and rewrote all it in Python, but the template format stayed the same because it was *simple*.


## Template variables

Given these basic assumptions:

- the latest tag is `v0.4.9`
- the NEXT version numbers have been defined to be `0.4.10`
- the actual commit count is `2`

Here is the list of variables, with their values, available for templates:

    ${CURRENT_VERSION}     = 0.4.10-SNAPSHOT-2/a3a73a58
    ${BUILD_ID}            = a3a73a58
    ${FULL_BUILD_ID}       = a3a73a5861e5721055f3a12545201e265ba0c097
    ${MAJOR}               = 0
    ${MINOR}               = 4
    ${PATCH}               = 10
    ${COMMIT_COUNT}        = 2
    ${COMMIT_COUNT_STR}    = 2 (or an empty string if 0)
    ${COMMIT_COUNT_PREFIX} = either the 'commit_count_prefix' specified in the config file or an empty string, if the commit count is 0
    ${META_PR}             = either the pre-release metadata from the last reachable tag, the 'default_meta_pr_in_next' (from config file), the 'default_meta_pr_in_next_no_next' (from config file) or an empty string, depending on the state of the repository
    ${META_PR_PREFIX}      = either the 'meta_pr_prefix' specified in the config file or an empty string, if no pre-release metadata is available for use

The list could later be expanded and improved, to cover much more information, such as date, time, let me know your suggestion!


## Compiling templates

In order to build or compile a template, you have to invoke *gitver*'s `update` command, followed by the template name(s):

    $ gitver update my_template


You can define any number of templates for the repository, just put them in the ```.gitver/templates``` directory: you can also tell *gitver* to build multiple templates at once by enclosing the list in quotes:

    $ gitver update "template1 template2 templateN"

To list the available templates, use the `list-templates` command:

    $ gitver list-templates
    Available templates:
        version (.gitver/templates/version)


## Template example

In a Python project of mine, this is the template "version" i've put in the `.gitver/templates` directory:

    # /home/manuel/dev/python/project/version.py
    #!/usr/bin/env python2
    # coding=utf-8
    
    # MACHINE-GENERATED CODE, DO NOT TOUCH!
    project_version = "v${CURRENT_VERSION}"
    project_build_id = "${FULL_BUILD_ID}"

Now let's compile it:

    $ gitver update version
    Processing template "version" for /home/manuel/dev/python/project/version.py...
    Done, 188 bytes written.


This will produce the following file at ```/home/manuel/dev/python/project/version.py```, **overwriting** the previous file, if any:

    #!/usr/bin/env python2
    # coding=utf-8
    
    # MACHINE-GENERATED CODE, DO NOT TOUCH!
    project_version = "v0.4.10-SNAPSHOT-2/a3a73a58"
    project_build_id = "a3a73a5861e5721055f3a12545201e265ba0c097"
   

## Templates + git hooks

At this point is very simple to automatize even more, instead of manually updating version information after each commit, let's create a git hook to take care of this:

    $ cat .git/hooks/post-commit 
    #!/bin/bash
    # gitver should be in your path to work!
    gitver update version

There you have it!


## Bugs
![bugs](http://media.giphy.com/media/10EdqIfzllpg6A/giphy.gif)

NOPE!! MY CODE HAS NO BUGS!11

Just joking, probably quite a few, please report them [here](https://github.com/manuelbua/gitver/issues), thanks!
