## What is it?
A very simple, lightweight, tag-based version string manager for git written in Bash.

#### Generates new version numbers
By *bumping* the version operands (*major*, *minor* and *patch*) described by a git tag, it will compute the next possible future version strings.

#### Helps in version management house-keeping

Coupled with [*git hooks*](http://git-scm.com/book/en/Customizing-Git-Git-Hooks), gitver version blob templates helps to keep your own project updated with its version information, performing simple keyword substitution automatically at *post-commit* time, for example.

## Why?
I'm working on a project that requires precise version string tracking and synchronization, so an automatic mechanism is needed.

Furthermore, i want the version string and/or other useful information to be **embedded** in the application code automatically, also known as "compiled-in" so to speak, without me having to remember to do it manually each time.

## Workflow

- verify your repository's tags are **not** already being used for some other purpose
- ```gitver init```, create first v0.0.1-SNAPSHOT version tag
- work on your project
- do a release, ```gitver finalize-bump```
- ***optional*** ```gitver update-versioninfo <template_name>``` to update version information in your project tree, then rebuild the project to reflect version changes
- any other manual house-keeping in-between releases can be performed now
- finally, decide to bump for next release cycle, e.g. ```gitver bump-patch```

## Basic usage 
**Note this is a preliminary version and both the configuration and the behavior are subject to change.**

    $ gitver
    Please run "gitver init" first.
    usage: gitver <init|info|bump-major|bump-minor|bump-patch|finalize-bump|update-versioninfo <template|template1 template2 templateN>>

The script expects the tags in your repository to be used to describe version information in the format ```vX.Y.Z``` or ```vX.Y.Z-SNAPSHOT```, so expect your repo tags to be used this way.
CUrrently, if no tags in this format are found, an error message will ask you to create one.

So, pick any repository you want to test this tool on and run ```gitver``` from the project root, if your repository doesn't have any tag yet you'll be asked to create one at HEAD:

    $ gitver init
    Created configuration directory "./.gitver"
    Created template directory "./.gitver/templates"
    This repository requires ANY tag to be in the format vX.Y.Z or vX.Y.Z-SNAPSHOT
    (TODO custom suffix in config)
    
    An initial first tag is needed, you can create such first tag with the following command:
        git tag -a v0.0.1-SNAPSHOT -m 'Initial version'
    
    Would you like to do it now at HEAD (y/n)? y
    Done.

At this point, *gitver* should be able to find it and produce some useful output:

    $ gitver info
    Current tag: v0.0.1-SNAPSHOT
    Current build ID: 9c5f36f9f0c940ba784134b5f5ba8bdf80d23947
    Current version: v0.0.1-SNAPSHOT/9c5f36f9
    Possible next versions to bump to:
      bump-major => v1.0.0-SNAPSHOT
      bump-minor => v0.1.0-SNAPSHOT
      bump-patch => v0.0.2-SNAPSHOT
    State: pending finalize, v0.0.1-SNAPSHOT => v0.0.1

As you can see, *gitver* found the tag and performed some work already: the current tag is shown and, transforming that in the format ```v<MAJ>.<MIN>.<PATCH>-<NOTES>/<HASH>```, it produced the current version string:

    Current version: v0.0.1-SNAPSHOT/9c5f36f9

Followed by computing the next possible version iteration strings:

    Possible next versions to bump to:
      bump-major => v1.0.0-SNAPSHOT
      bump-minor => v0.1.0-SNAPSHOT
      bump-patch => v0.0.2-SNAPSHOT

This means *gitver* can automatically bump maj/min/patch versions via the command line switches, whenever the time for release has came and a new iteration will (hopefully!) begin.

So let's suppose you now want to release the stable version, you'll remember how smart *gitver* is :) and recall that ```gitver info``` also described that:

    State: pending finalize, v0.0.1-SNAPSHOT => v0.0.1

That is, *gitver* will costantly remember you which version you are working on and what version you are going to finalize things to, so just do it:

    $ gitver finalize-bump
    Done, v0.0.1-0-g9c5f36f

Now *gitver* should have created another tag all by itself, v0.0.1:

    $ git tag
    v0.0.1
    v0.0.1-SNAPSHOT

    $ gitver info
    Current tag: v0.0.1
    Current build ID: 9c5f36f9f0c940ba784134b5f5ba8bdf80d23947
    Current version: v0.0.1/9c5f36f9
    Possible next versions to bump to:
      bump-major => v1.0.0-SNAPSHOT
      bump-minor => v0.1.0-SNAPSHOT
      bump-patch => v0.0.2-SNAPSHOT
    State: version idleing (v0.0.1)

*gitver* noticed there are no SPANSHOT-suffixed tags, thus versioning is happily idleing: as soon as you bump for the next release cycle, versioning is resumed:

    $ gitver bump-patch
    Bumping from v0.0.1 to 0.0.2-SNAPSHOT
    Done, v0.0.2-SNAPSHOT-0-g9c5f36f

    $ gitver info
    Current tag: v0.0.2-SNAPSHOT
    Current build ID: 9c5f36f9f0c940ba784134b5f5ba8bdf80d23947
    Current version: v0.0.2-SNAPSHOT/9c5f36f9
    Possible next versions to bump to:
      bump-major => v1.0.0-SNAPSHOT
      bump-minor => v0.1.0-SNAPSHOT
      bump-patch => v0.0.3-SNAPSHOT
    State: pending finalize, v0.0.2-SNAPSHOT => v0.0.2

    $ git tag
    v0.0.1
    v0.0.1-SNAPSHOT
    v0.0.2-SNAPSHOT

The way it works could put some people off i think, i suspect not everyone is ok with tag proliferation, and thus real commit objects, but in my opinion this is something i'm willing to pay for, if this mechanism can pushed even further, and sure it can be.

## Template-based version information blobs
One of the main reasons for this script to exists is to be able to also automatically update the project own's version information blob (e.g. ```VersionInfo.java```).

I usually keep it *excluded* from the repository itself with a ```.gitignore``` directive since there would be no point in tracking it but also it would be impossible to know the hash in advance for the next build since that isn't a predictable incremental number.

## Template format
The only **required** bit of information *gitver* needs is where the output of this template should be placed, so the first line shall only contain the path to the output file in a Bash-style comment (spaces are trimmed):

    # /path/to/project/file.extension

The rest of the file is obviously up to you, an example is available at the "Template example" section.

## Template variables
Currently, the following variables are available to the template, depicted here are their names and values given an imaginary tag, such as "v0.4.10-SNAPSHOT":

    - ${CURRENT_VERSION} = 0.4.10-SNAPSHOT-1/bb29217d
    - ${BUILD_ID}        = bb29217d
    - ${FULL_BUILD_ID}   = bb29217d46325ba4f7b8177c9cc1cddd82246f32
    - ${MAJOR}           = 0
    - ${MINOR}           = 4
    - ${PATCH}           = 10
    - ${NOTE}            = SNAPSHOT
    - ${NEXT_MAJOR}      = 1.0.0-SNAPSHOT
    - ${NEXT_MINOR}      = 0.5.0-SNAPSHOT
    - ${NEXT_PATCH}      = 0.4.11-SNAPSHOT
    - ${COMMIT_COUNT}    = 1

Technically, more information shall be available due to the nature of this very basic templating system, but those are the most useful, lookup the source for others.

## Template invokation
In order to perform keyword substitution, you have to invoke *gitver* with the ```update-versioninfo``` switch, followed by the template name(s):

    $ gitver update-versioninfo my_template

You can define any number of templates for the repository, just put them in the ```.gitver/templates``` directory: then you can specify multiple templates at once by enclosing the list in quotes (e.g. ```"this another_one the_third"```).


## Template example
In a Python project of mine, this is the template "test" i put in its ```.gitver/templates``` directory:

    # /home/manuel/dev/python/project/version.py
    #!/usr/bin/env python2
    # coding=utf-8
    
    # MACHINE-GENERATED CODE, DO NOT TOUCH!
    project_version = "v${CURRENT_VERSION}"
    project_build_id = "${FULL_BUILD_ID}"

Now let's invoke *gitver* to perform keyword substitution on that template:

    $ gitver update-versioninfo test
    Processing "./.gitver/templates/test", wrote file file:///home/manuel/dev/python/project/version.py (4.0K)

This will produce the following file at ```/home/manuel/dev/python/project/version.py```, **overwriting** the previous file, if any:

    #!/usr/bin/env python2
    # coding=utf-8
    
    # MACHINE-GENERATED CODE, DO NOT TOUCH!
    project_version = "v0.4.10-SNAPSHOT-1/bb29217d"
    project_build_id = "bb29217d46325ba4f7b8177c9cc1cddd82246f32"

## Templates + git hooks
At this point is very simple to automatize even more, instead of manually updating version information after each commit let's create a git hook to take care of it:

    $ cat .git/hooks/post-commit 
    #!/bin/bash
    # gitver should be in your path to work!
    gitver update-versioninfo test

There you have it!

## Bugs
NOPE!! MY CODE HAS NO BUGS!11

But please report them [here](https://github.com/manuelbua/gitver/issues), thanks!

# Future plans
I'm probably going to rewrite this in Python with the awesome [sh](https://github.com/amoffat/sh) library, but for now it does the job nicely.
