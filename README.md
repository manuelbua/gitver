[![PyPi version](https://pypip.in/v/gitver/badge.png)](https://crate.io/packages/gitver/)
[![PyPi downloads](https://pypip.in/d/gitver/badge.png)](https://crate.io/packages/gitver/)
[![Project Stats](https://ohloh.net/p/gitver/widgets/project_thin_badge.gif)](https://ohloh.net/projects/gitver)
[![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=manuelbua&url=https://github.com/manuelbua/gitver&title=gitver&language=&tags=github&category=software)


## What is it?
A very simple, lightweight, tag-based version string manager for git, written in Python.

It generates version strings by using Python-based formatting rules coupled with repository information, augmented by user-defined data.

It supports up to four different version number operands and optional pre-release version information, in the format `[v]MAJOR.MINOR.PATCH[.REVISION][-PRE-RELEASE-METADATA]`, making to adopt versioning schemes such as [Semantic Versioning](https://semver.org) a breeze.

Optionally, it also keeps your project's version information blobs automagically updated via custom templates.

Sample output (this repository):

    Most recent tag: v0.3.0-RC1
    (NEXT defined as: 0.3.0)
    Using pre-release metadata: RC1
    Current build ID: 1d170e7f42817d0f277c52ad686b24ac69b353d4
    Current version: v0.3.0-RC1.47+1d170e7 => v0.3.0


## Installation

Please read the simple *Installation instructions* in the [INSTALL.md](https://github.com/manuelbua/gitver/blob/master/INSTALL.md) file, you can install either via `pip` or by cloning this repository.

*NOTE the **badges** present at the top of these pages (version and downloads) refers to the latest stable packages uploaded to PyPI: cloning this repository will checkout the version i'm currently working on and may not reflect the same version.*


## Helps in version string management

Coupled with [git hooks](http://git-scm.com/book/en/Customizing-Git-Git-Hooks), `gitver` version blob templates helps to keep your own project updated with its version information, performing simple template-based substitution automatically at *post-commit* time, for example.


## Why?

I'm working on a project that requires precise version string tracking and synchronization between a server and its different clients, so an automatic mechanism is needed.

Furthermore, i want the version string and/or other useful information to be **embedded** in the application code automatically, "compiled-in" so to speak, without me having to remember to do it manually each time.


## Repository pre-requisites

`gitver` expects your tags to be **annotated** and be in this format:

    [v]MAJOR.MINOR.PATCH[.REVISION][-PRE-RELEASE-METADATA]

Text in `[` square brackets `]` is optional, so these example tags are all valid for use with `gitver`:

    v0.0.1
    0.0.1-RC0
    v0.0.1-RC2

Note that, at this time, `gitver` will **not** skip unsupported tags during its processing, so whenever it encounter such malformed tags (i.e. "this-is-my-tag") it will just error out something like this:

    ERROR: Couldn't retrieve version information from tag "my-other-tag".
    gitver expects tags to be in the format [v]X.Y.Z[.REVISION][-PRE-RELEASE-METADATA]

However, since `gitver` will only search for annotated tags, you could safely use *unannotated tags* for any other need.


## Workflow

Your workflow shouldn't change much from what you are used to, but before using it, please review the "Repository pre-requisites" section above and ensure your tags are not already being used for some other purpose.

*Note that `gitver` will **never** tag, commit or interact in write-mode with your repository in any way, ever!*

The following is a workflow exemplification of using *gitver* to manage version strings for your project, given it has already been setup:

- you are working on your repository, now you are ready to promote the current version to the next release
- create a release tag, `git tag -a v0.0.2 -m 'Bump version'`
- defines your NEXT version, the one you are going to work *towards* to by running `gitver next 0.0.3`
- run `gitver` and check everything is fine
- **OPTIONAL** preview or update your project's version information templates by running `gitver preview <template name>` or `gitver update <template name>`, then rebuild the project to reflect version changes
- any other manual house-keeping in-between releases can be performed now
- now you are working towards the NEXT release, repeat when release time has came again


## How does it work?

By reading your last reachable **annotated** tag, it will generate customly-formatted version strings, distinguishing automatically between *stable* and *development* builds, depending on the number of commits from that last tag (the *commit count*).

It will also apply tag-based or configuration file-based pre-release metadata in development builds, giving you fine-grained control on how the final version string will be composed.


## Config file

`gitver` uses a per-repository, JSON-based configuration file.

The default configuration file gets created automatically in `.gitver/config` and it contains the following tweakable settings:

    {
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
    }
This file gets created automatically in your `.gitver` directory when you initialize it with the `gitver init` command: should you need to regenerate it, for example after updating to a `gitver` release that adds more configuration options (this will be noted in the ChangeLog or by other means), you just need to move/delete the old configuration and trigger regeneration by re-issuing the init command.

## Basic usage 

    $ gitver --help
    usage: gitver [-h] [--ignore-gitignore] [--colors {config,yes,no}] [--quiet]
                  [--quiet-errors]
                  
                  {version,init,check,info,current,list-templates,list-next,update,preview,next,clean,clean-all}
                  ...

    optional arguments:
      -h, --help            show this help message and exit
      --ignore-gitignore    Ignore the .gitignore warning and continue running as
                            normal (specify this flag before any other command, at
                            YOUR own risk)
      --colors {config,yes,no}
                            Enable or disable colorized terminal output: 'config'
                            (default) reads the setting from your configuration
                            file, 'yes' will force-enable it, 'no' will force-
                            disable it.
      --quiet               Disable any stdout message.
      --quiet-errors        Disable any stderr message.

    Valid commands:
      {version,init,check,info,current,list-templates,list-next,update,preview,next,clean,clean-all}
        version             Shows gitver version
        init                Creates gitver's configuration directory and creates
                            the default configuration file, if it doesn't exist.
        check               Checks your .gitignore file for gitver's configuration
                            directory inclusion.
        info                Prints full version information and tag-based metadata
                            for this repository. [default]
        current             Prints the current version information only, without
                            any formatting applied.
        list-templates      Enumerates available templates.
        list-next           Enumerates user-defined next stable versions.
        update              Performs simple keyword substitution on the specified
                            template file(s) and place it to the path described by
                            the first line in the template. This is usually
                            performed *AFTER* a release has been tagged already.
        preview             Same as "update", but the output is written to the
                            stdout instead (same rules apply).
        next                Defines the next stable version for the most recent
                            and reachable tag.
        clean               Removes the user-defined next stable version for the
                            most recent and reachable tag or the specified tag.
        clean-all           Removes ALL user-defined next stable versions.


### Introduction

The following is an easy-to-follow, step-by-step mini tutorial that will walk you through the features of `gitver`: we are going to create a brand new repository at `/tmp/test` for this.


### Step-by-step mini tutorial

##### Building some repository history

Let's create a new repository in your `/tmp` folder:

    cd /tmp && mkdir test && cd test && git init

Now populate it with some activity:

    echo "some data" > some && git add some && git commit -m 'initial commit' && echo "more data" > more && echo "another one" > another && git add more && git commit -m 'one more' && git add another && git commit -m 'even more'

Your repository should now look like this:

    * b01e958  (HEAD, master) (Thu Jan 16 17:08:54 2014) even more (Manuel Bua)
    * 8f5862b  (Thu Jan 16 17:08:54 2014) one more (Manuel Bua)
    * fac3511  (Thu Jan 16 17:08:54 2014) initial commit (Manuel Bua)

Let's initialize `gitver` at this point:

    $ gitver init
    gitver has been initialized and configured.

`gitver` just created its own `.gitver` configuration directory and generated the default configuration file `config` right there. At this point it's recommended, but not mandatory, to **exclude** gitver's configuration directory from the repository by adding it to your `.gitignore` file: this is to prevent losing your `gitver`'s configuration whenever you checkout old revisions of your project.

Anyway, the tool is quite smart in that and it will *not* proceed if it detects potential problems with the command you issued, in case your `.gitignore` file isn't properly setup, so let's run a check at this point to see that warning message:

    $ gitver check
    Your .gitignore file doesn't define any rule for the .gitver
    configuration directory: it's recommended to exclude it from
    the repository, unless you know what you are doing. If you are not
    sure, add this line to your .gitignore file:

        .gitver

So let's create your ignore file, add that line, then run `gitver`:

    $ echo ".gitver" >> .gitignore
    $ gitver
    ERROR: Couldn't retrieve the latest tag

Right, we have no tags at this point, so let's create `v0.0.0` at the first commit with this command (replace the commit hash with your own where needed):

    git tag -a v0.0.0 -m 'Initial version' fac3511

This is how your repository should look like:

    * b01e958  (HEAD, master) (Thu Jan 16 17:08:54 2014) even more (Manuel Bua)
    * 8f5862b  (Thu Jan 16 17:08:54 2014) one more (Manuel Bua)
    * fac3511  (tag: v0.0.0) (Thu Jan 16 17:08:54 2014) initial commit (Manuel Bua)

Now `gitver` output should be somewhat more informative:

    Most recent tag: v0.0.0
    Using NEXT defined as: none, defaulting to -NEXT suffix
    (Pre-release metadata: none)
    Current build ID: b01e95831e8c240415510be16e93e10f68fb964a
    Current version: v0.0.0-NEXT.2+b01e958

Time to decide what the NEXT version numbers will be, so let's set this and run `gitver` again:

    $ gitver next 0.0.1
    Set NEXT version string to 0.0.1 for the current tag v0.0.0

    $ gitver
    Most recent tag: v0.0.0
    Using NEXT defined as: 0.0.1
    (Pre-release metadata: none)
    Current build ID: b01e95831e8c240415510be16e93e10f68fb964a
    Current version: v0.0.1-SNAPSHOT.2+b01e958 => v0.0.1

Notice how the build id stayed the same but the version string changed: both strings describes the same point in development, they are *equivalent*, but given the same descriptive intentions, i find the latter to be much more clear.

Now lookup your `.gitver/config` file and look at the `format_next` definition:

    "format_next": "%(maj)s.%(min)s.%(patch)s%(rev_prefix)s%(rev)s%(meta_pr_prefix)s%(meta_pr)s%(commit_count_prefix)s%(commit_count)s+%(build_id)s"

This defines the format of the version string being generated at this point of development: since the *commit count* from the most recent valid tag is greater than `0`, this denotes a *development* build, and the `format_next` variation is used: the `%(meta_pr)s` placeholder will be replaced by the pre-release metadata if your tag defines one, else the configuration defaults will be used, but this will only happen in development builds, there is no point in exposing *pre-release* metadata in a *stable* release.

The `%(meta_pr_prefix)s` counterpart, instead, will be filled with the value of `meta_pr_prefix` *only* if pre-release metadata is used, else it will be set to an empty string as well.

The same reasoning applies to the *commit count*: whenever it's equal to `0` both `%(commit_count)s` and `%(commit_count_prefix)s` will be set to an empty string.

This permit to adapt and change version string formats by letting you defines concatenations more easily.


##### Tagging a release

Let's add that `.gitignore` file we didn't add before, then declare the version stable by just tagging it as that:

    $ git add .gitignore && git commit -m 'Add .gitignore file'
    $ git tag -a 'v0.0.1' -m 'Bump version'

Your repository should now look like this:

    * 3a3cf5f  (HEAD, tag: v0.0.1, master) (Thu Jan 16 17:29:00 2014) Add .gitignore file (Manuel Bua)
    * b01e958  (Thu Jan 16 17:08:54 2014) even more (Manuel Bua)
    * 8f5862b  (Thu Jan 16 17:08:54 2014) one more (Manuel Bua)
    * fac3511  (tag: v0.0.0) (Thu Jan 16 17:08:54 2014) initial commit (Manuel Bua)

So let's have `gitver` take a look at the repository now: 

    $ gitver
    Most recent tag: v0.0.1
    Current build ID: 3a3cf5ffe0a6a2f6051420ac730554c92bf9bdf2
    Current version: v0.0.1

As you can see, `gitver` now uses the *other* string format from the configuration file:

    "format": "%(maj)s.%(min)s.%(patch)s%(rev_prefix)s%(rev)s%(meta_pr_prefix)s%(meta_pr)s"

This is being used when the commit count from the most recent tag is equal to `0` since this denotes a *stable* build, rather than a development one.

Depending on your project, format strings can change slightly between *stable* and *development* versions: `gitver` gives you full control over what format to use in each case.

For completeness, let's use the `format_next` format for the stable build as well and edit that portion of your configuration file to look like this:

    "format": "%(maj)s.%(min)s.%(patch)s%(meta_pr_prefix)s%(meta_pr)s%(commit_count_prefix)s%(commit_count)s+%(build_id)s"

Done that? Now look at `gitver`'s output now:

    $ gitver
    Most recent tag: v0.0.1
    Current build ID: 94b2ef2ed92844377f1e8b1160a014bae0273792
    Current version: v0.0.1+94b2ef2

As expected, there is no sign of prefixes, nor default metadata or commit count in the stable build.


## Template-based version information blobs

One of the main reasons for this tool to exists is to be able to also automatically update your project own's version information *blob* (e.g. `VersionInfo.java`, `version.py`, ...) or some other external file with the project's version information.


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

Here is the list of variables, with their values, available for use in templates:

    ${CURRENT_VERSION}     = 0.4.10-SNAPSHOT-2/a3a73a58
    ${BUILD_ID}            = a3a73a58
    ${FULL_BUILD_ID}       = a3a73a5861e5721055f3a12545201e265ba0c097
    ${MAJOR}               = 0
    ${MINOR}               = 4
    ${PATCH}               = 10
    ${REV}                 = (empty string, or a revision number if present)
    ${REV_PREFIX}          = (empty string, or a '.' if a revision number is present)
    ${COMMIT_COUNT}        = 2 (or 0 if commit count is 0)
    ${COMMIT_COUNT_STR}    = '2' (or an empty string if commit count is 0)
    ${COMMIT_COUNT_PREFIX} = either the 'commit_count_prefix' specified in the config file or an empty string, if the commit count is 0
    ${META_PR}             = either the pre-release metadata from the last reachable tag, the 'default_meta_pr_in_next' (from config file), the 'default_meta_pr_in_next_no_next' (from config file) or an empty string, depending on the state of the repository
    ${META_PR_PREFIX}      = either the 'meta_pr_prefix' specified in the config file or an empty string, if no pre-release metadata is available for use

The list could later be expanded and improved, to cover much more information, such as date, time, let me know your suggestion!


## Previewing and compiling templates

You can preview the result of the template substitution by using the `preview`command, followed by one or more template names (multiple template names should be quoted):

    $ gitver preview my_template
                or
    $ gitver preview "template1 template2 templateN"

This will process the template and print the output to the stdout instead of writing it to a file: this can be useful for scripting purposes, where you can filter out information messages while only capturing the "real meat":

    $ gitver preview my_template 2>/dev/null

The `update` command works similarly, it will just write the output to the specified file, rather than stdout:

    $ gitver update my_template
                or
    $ gitver update "template1 template2 templateN"

It's possible to define any number of templates, just put them in the `.gitver/templates` directory: to have `gitver` enumerate all the available templates, use the `list-templates` command:

    $ gitver list-templates
    Available templates:
        version (/home/manuel/dev/gitver/.gitver/templates/version)
        test (/home/manuel/dev/gitver/.gitver/templates/test)


## Template example

Let's take a look at `gitver`'s own [template](hub.com/manuelbua/gitver/blob/master/.gitver/templates/version):

    # gitver/_version.py
    #!/usr/bin/env python2
    # coding=utf-8

    # DO NOT TOUCH, AUTOMATICALLY UPDATED!
    gitver_version = '${CURRENT_VERSION}'
    gitver_buildid = '${FULL_BUILD_ID}'
    gitver_pypi = '${MAJOR}.${MINOR}.${PATCH}${META_PR_PREFIX}${META_PR}${COMMIT_COUNT_PREFIX}${COMMIT_COUNT_STR}'

Now let's compile it:

    $ gitver update version
    Processing template "version" for /home/manuel/dev/gitver/gitver/_version.py...
    Done, 207 bytes written.

This will produce the following file at `/home/manuel/dev/gitver/gitver/_version.py`, **overwriting** the previous file, if any:

    #!/usr/bin/env python2
    # coding=utf-8

    # DO NOT TOUCH, AUTOMATICALLY UPDATED!
    gitver_version = '0.3.0-RC1.47+1d170e7'
    gitver_buildid = '1d170e7f42817d0f277c52ad686b24ac69b353d4'
    gitver_pypi = '0.3.0-RC1.47'
   

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
