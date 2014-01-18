[![PyPi version](https://pypip.in/v/gitver/badge.png)](https://crate.io/packages/gitver/)
[![PyPi downloads](https://pypip.in/d/gitver/badge.png)](https://crate.io/packages/gitver/)
[![Project Stats](https://ohloh.net/p/gitver/widgets/project_thin_badge.gif)](https://ohloh.net/projects/gitver)
[![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=manuelbua&url=https://github.com/manuelbua/gitver&title=gitver&language=&tags=github&category=software)

# Installation instructions

`gitver` can be installed either via `pip` or by checking out the repositroy, the place where all the development happens.

By using the latter you'll be able to choose between *stable* or *development* releases, while on [PyPI](https://pypi.python.org/pypi) only stable versions are uploaded.

*NOTE the **badges** present at the top of these pages (version and downloads) refers to the latest stable packages uploaded to PyPI: cloning this repository will checkout the version i'm currently working on and may not reflect the same version.*

## Requirements

#### Environment

You'll need these packages to be installed, usually by your OS' package manager:

- Python 2.7 (2.6 *may* works, but i've not tested it)
- the `git` tool


## Install via PyPI

If you don't have `pip` installed, let's do that now: there are various ways to do that, i personally prefer to use my OS package manager.

For Arch Linux installations, you may install `pip` system-wide with this command:

    sudo pacman -S python2-pip

When finished, check everything is fine:

    $ pip2 --version
    pip 1.5 from /usr/lib/python2.7/site-packages (python 2.7)

Now you are ready to install via `pip`:

    $ pip2 install gitver

Done!

## Install via repository

You are going to need to install `setuptools` and `pip`, so use your package manager or any other means for this.

For Arch Linux installations, you may install them system-wide with this command:

    sudo pacman -S python2-setuptools python2-pip

Refer to your package manager of choice on how to do that.

#### Clone the project

When done, you can proceed to clone the project from [github](https://github.com/manuelbua/gitver):

    git clone git@github.com:manuelbua/gitver.git gitver.git

#### Setup git hooks

`gitver` uses itself to keep track of version information, so let's setup git hooks to perform that automatically at `post-checkout` and `post-commit` time.

We are going to create soft-links in your `.git/hooks` directory to point to the `gitver.git/hooks/post-commit` script, so let's do that:

    $ cd gitver.git/.git/hooks
    $ ln -s ../../hooks/post-commit post-commit
    $ ln -s ../../hooks/post-commit post-checkout

At this point you should have two new git hooks configured, along with some git's own samples:

    $ ls -la
    total 40
    drwxr-xr-x 2 manuel users  260 Jan 18 18:16 .
    drwxr-xr-x 8 manuel users  260 Jan 18 18:10 ..
    -rwxr-xr-x 1 manuel users  452 Jan 18 18:10 applypatch-msg.sample
    -rwxr-xr-x 1 manuel users  896 Jan 18 18:10 commit-msg.sample
    lrwxrwxrwx 1 manuel users   23 Jan 18 18:16 post-checkout -> ../../hooks/post-commit
    lrwxrwxrwx 1 manuel users   23 Jan 18 18:16 post-commit -> ../../hooks/post-commit
    -rwxr-xr-x 1 manuel users  189 Jan 18 18:10 post-update.sample
    -rwxr-xr-x 1 manuel users  398 Jan 18 18:10 pre-applypatch.sample
    -rwxr-xr-x 1 manuel users 1642 Jan 18 18:10 pre-commit.sample
    -rwxr-xr-x 1 manuel users 1239 Jan 18 18:10 prepare-commit-msg.sample
    -rwxr-xr-x 1 manuel users 1352 Jan 18 18:10 pre-push.sample
    -rwxr-xr-x 1 manuel users 4951 Jan 18 18:10 pre-rebase.sample
    -rwxr-xr-x 1 manuel users 3611 Jan 18 18:10 update.sample

We now gained automatic version information update: as soon as you `checkout` or `commit` something, the file `gitver/_version.py` will be created/overwritten with the updated `gitver`'s version information.

#### Install project requirements

Now we should satisfy the project's requirements and we'll do that with `pip`: i'm going to do a system-wide installation at this point, but you may choose to use `virtualenv` as well, it shouldn't be a problem should you choose that way:

    $ cd gitver.git
    $ sudo pip2 install -r requirements.txt

At this point, you should be ready to run `gitver` directly from the repository:

    $ bin/gitver version
    This is gitver n/a
    Full build ID is n/a
    ...

You probably noticed there is no version information there, this will be done automatically when installing, but for now let's generate it manually:

    $ bin/gitver update version
    Processing template "version" for /tmp/gitver.git/gitver/_version.py...
    Done, 207 bytes written.

    $ bin/gitver version
    This is gitver v0.3.0-RC1.69+8f975ed
    Full build ID is 8f975ed5c1195038f71db36ccc6c1c5b2b8cacd3
    ...

Nice! Things are working fine at this point, let's install it system-wide now:

    $ ./install_dev

A couple of lines should be output to your stdout, but ultimately you should be able to locate the `gitver` executable in your system's bin directory:

    $ which gitver
    /usr/bin/gitver

Done! You can now start hacking on the code, build awesome new stuff and submit new features to me as pull-request as well.