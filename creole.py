#!/usr/bin/env python
"""Pycreole - a simple web crawler."""

__author__ = "Filip Salomonsson <filip@infix.se>"

import urllib2

if __name__ == '__main__':
    import sys

    url = sys.argv[1]
    res = urllib2.urlopen(url)
    data = res.read()
    print data
