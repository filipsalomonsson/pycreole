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
    op.add_option("-s", "--store", dest="store", default=".",
                  help="storage directory")
    op.add_option("-d", "--delay", dest="delay", default="1",
                  type="int", help="throttle delay")
    (options, args) = op.parse_args()

    # We need at least one URL
    if len(args) < 1:
        op.error("no URL given")

    # Create a crawler and send it off.
    crawler = Crawler(store=options.store,
                      throttle_delay=options.delay)
    crawler.crawl(args[0])
