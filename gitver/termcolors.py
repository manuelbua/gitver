#!/usr/bin/env python2
# coding=utf-8

"""
Provides stdout/stderr output, with optional color output, if supported
"""

import sys
import os


# Color support via ansicolors package
try:
    from colors import color

    def color_tag(text):
        return color(text, fg=231, bg=239, style='bold')

    def color_next(text):
        return color(text, fg=231, bg=28, style='bold')

    def color_version(text):
        return color(text, fg=255, bg=25, style='bold')

    def color_promoted(text):
        return color(text, fg=255, bg=33, style='bold')

    def color_warn(text):
        return color(text, fg=214, style='bold')

    def color_err(text):
        return color(text, fg=196, style='bold')

    def bold(text):
        return color(text, style='bold')

except ImportError:

    def color_tag(text):
        return text

    def color_next(text):
        return text

    def color_version(text):
        return text

    def color_warn(text):
        return text

    def color_err(text):
        return text

    def bold(text):
        return text


class Terminal(object):
    def __init__(self):
        self.__use_colors = False

    def enable_colors(self, use_colors):
        self.__use_colors = use_colors

    def are_colors_enabled(self):
        return self.__use_colors

    def __emit(self, text, stream, func):
        if self.__use_colors:
            stream.write(func(text + os.linesep))
        else:
            stream.write(text + os.linesep)

    def __decorate(self, text, func):
        if self.__use_colors:
            return func(text)
        else:
            return text

    def err(self, text):
        self.__emit(text, sys.stderr, color_err)

    def warn(self, text):
        self.__emit(text, sys.stderr, color_warn)

    def prn(self, text):
        sys.stdout.write(text + os.linesep)

    def tag(self, text):
        return self.__decorate(text, color_tag)

    def next(self, text):
        return self.__decorate(text, color_next)

    def ver(self, text):
        return self.__decorate(text, color_version)

    def prom(self, text):
        return self.__decorate(text, color_promoted)

term = Terminal()
