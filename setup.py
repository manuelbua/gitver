#!/usr/bin/env python2
# coding=utf-8

import sys

try:
    import pypandoc
except ImportError:
    print "The \"pypandoc\" package and the pandoc binary on your system " \
          "need to be present to run setuptools."
    sys.exit(1)


from setuptools import setup
from gitver.version import gitver_version, gitver_pypi

try:
    import gitver._version_next as next
    vtype = '(NEXT)'
except ImportError:
    vtype = '(RELEASE)'


def readme():
    return pypandoc.convert('README.md', 'rst')


def requirements():
    with open('requirements.txt') as f:
        return f.read()


def main():
    """Runs setuptools.setup()"""

    scripts = [
        'bin/gitver'
    ]

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
        author_email='manuel.bua@gmail.com',
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
