#!/usr/bin/env python
"""Pycreole - a simple web crawler."""

__author__ = "Filip Salomonsson <filip@infix.se>"
__version__ = "0.1a"

USER_AGENT = "pycreole"

if __name__ == '__main__':
    import sys
    from optparse import OptionParser
    from creolelib.crawler import Crawler

    # Set up and run the option parser
    usage = "usage: %prog [options] URL ..."
    op = OptionParser(usage)
    op.add_option("-d", "--dir", dest="dir", default=".",
                  help="storage directory")
    (options, args) = op.parse_args()

    # We need at least one URL
    if len(args) < 1:
        op.error("no URL given")

    # Create a crawler and send it off.
    crawler = Crawler(store=options.dir)
    print crawler.crawl(args[0])
