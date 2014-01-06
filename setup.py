#!/usr/bin/env python2
# coding=utf-8

import os
import pypandoc
import sys
from setuptools import setup


def readme():
    return pypandoc.convert('README.md', 'rst')


def requirements():
    with open('requirements.txt') as f:
        return f.read()


def get_version():
    here = os.path.dirname(__file__)
    scope = {}

    version = os.path.join(here, 'gitver', 'version.py')
    try:
        exec(open(version).read(), scope)
        return scope['gitver_version']
    except IOError:
        print "Couldn't find any *release* version information, trying dev..."
        version = os.path.join(here, 'gitver', '_version.py')
        try:
            exec(open(version).read(), scope)
            return scope['gitver_version']
        except IOError:
            print "Couldn't find any *develop* version information, aborting"
            sys.exit(1)


def main():
    """Runs setuptools.setup()"""

    scripts = [
        'bin/gitver'
    ]

    setup(
        name='gitver',
        version=get_version(),
        description='Simple version string management for git',
        long_description=readme(),
        license='Apache License, Version 2.0',
        author='Manuel Bua',
        author_email='manuel.bua@gmail.com',
        url='https://github.com/manuelbua/gitver',
        scripts=scripts,
        packages=['gitver'],
        install_requires=requirements()
    )


if __name__ == '__main__':
    main()
