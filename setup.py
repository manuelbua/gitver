#!/usr/bin/env python2
# coding=utf-8

import sys
from setuptools import setup
from gitver.version import gitver_version, gitver_pypi

make_sdist = len({'sdist', 'build'} & set(sys.argv)) > 0

try:
    import gitver._version_next as next
    vtype = '(NEXT)'
except ImportError:
    vtype = '(RELEASE)'


def readme():
    if make_sdist:
        try:
            import pypandoc
            return pypandoc.convert('README.md', 'rst')
        except ImportError:
            print "Warning: the \"pypandoc\" package and/or the pandoc " \
                  "binary can't be found on your system: if you want to " \
                  "generate the README.rst for PyPI you'll need to install " \
                  "them properly, else a fallback description will be used."

    # falling back to a simple description
    return 'Simple version string management for git'


def requirements():
    with open('requirements.txt') as f:
        return f.read()


def main():
    """Runs setuptools.setup()"""

    scripts = [
        'bin/gitver'
    ]

    if make_sdist:
        print "--------------------------------------------------"
        print "Setting up for " + vtype + " v" + gitver_version
        print "--------------------------------------------------"

    setup(
        name='gitver',
        version=gitver_pypi,
        description='Simple version string management for git',
        long_description=readme(),
        license='Apache License, Version 2.0',
        author='Manuel Bua',
        author_email='manuel.bua[at]gmail.com',
        url='https://github.com/manuelbua/gitver',
        scripts=scripts,
        packages=['gitver'],
        install_requires=requirements(),
        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Version Control',
        ]
    )


if __name__ == '__main__':
    main()
