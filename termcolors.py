#!/usr/bin/env python2
# coding=utf-8

"""
Color support via ansicolors package
"""

try:
    from colors import color

    def color_tag(text):
        return color(text, fg=231, bg=239, style='bold')

    def color_next(text):
        return color(text, fg=231, bg=28, style='bold')

    def color_version(text):
        return color(text, fg=255, bg=25, style='bold')

    def warn(text):
        return color(text, fg=214, style='bold')

    def err(text):
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

    def warn(text):
        return text

    def err(text):
        return text

    def bold(text):
        return text
