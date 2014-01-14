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
    """
    Provides a way to output text to the stdout or stderr, optionally
    with colors.
    """
    def __init__(self):
        self.__use_colors = False
        self.is_quiet = False
        self.is_quiet_err = False

    def enable_colors(self, use_colors):
        self.__use_colors = use_colors

    def set_quiet_flags(self, quiet_stdout, quiet_stderr):
        self.is_quiet = quiet_stdout
        self.is_quiet_err = quiet_stderr

    def __emit(self, text, stream, func=None):
        if self.__use_colors and func is not None:
            stream.write(func(text + os.linesep))
        else:
            stream.write(text + os.linesep)

    def __decorate(self, text, func):
        if self.__use_colors:
            return func(text)
        else:
            return text

    def err(self, text):
        """
        Outputs an ERROR message to the stderr
        """
        if not self.is_quiet_err:
            self.__emit("ERROR: " + text, sys.stderr, color_err)

    def warn(self, text):
        """
        Outputs a WARNING message to the stderr
        """
        if not self.is_quiet_err:
            self.__emit("WARNING: " + text, sys.stderr, color_warn)

    def info(self, text):
        """
        Outputs an INFORMATIVE message to the stderr
        """
        if not self.is_quiet_err:
            self.__emit(text, sys.stderr, None)

    def out(self, text):
        """
        Outputs a message to the stdout
        """
        if not self.is_quiet:
            self.__emit(text, sys.stdout)

    def tag(self, text):
        """
        Decorate the specified text with the TAG color class
        """
        return self.__decorate(text, color_tag)

    def next(self, text):
        """
        Decorate the specified text with the NEXT color class
        """
        return self.__decorate(text, color_next)

    def ver(self, text):
        """
        Decorate the specified text with the VERSION color class
        """
        return self.__decorate(text, color_version)

    def prom(self, text):
        """
        Decorate the specified text with the PROMOTED color class
        """
        return self.__decorate(text, color_promoted)

term = Terminal()
