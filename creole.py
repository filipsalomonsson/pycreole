#!/usr/bin/env python
"""Pycreole - a simple web crawler."""

__author__ = "Filip Salomonsson <filip@infix.se>"

import urllib2

if __name__ == '__main__':
    import sys
    from optparse import OptionParser

    # Set up and run the option parser
    usage = "usage: %prog [options] URL ..."
    op = OptionParser(usage)
    op.add_option("-d", "--dir", dest="dir", help="storage directory")
    (options, args) = op.parse_args()

    # We need at least one URL
    if len(args) < 1:
        op.error("no URL given")

    # Fetch the requested URL and print its contents
    url = args[0]
    res = urllib2.urlopen(url)
    data = res.read()
    print data
