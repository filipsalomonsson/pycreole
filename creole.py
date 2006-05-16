#!/usr/bin/env python
"""Pycreole - a simple web crawler."""

__author__ = "Filip Salomonsson <filip@infix.se>"

import urllib2

if __name__ == '__main__':
    import sys
    from optparse import OptionParser
    import urlparse
    import re
    import os.path
    import md5

    # Set up and run the option parser
    usage = "usage: %prog [options] URL ..."
    op = OptionParser(usage)
    op.add_option("-d", "--dir", dest="dir", default=".",
                  help="storage directory")
    (options, args) = op.parse_args()

    # We need at least one URL
    if len(args) < 1:
        op.error("no URL given")

    # Clean up the URL (get rid of any fragment identifier)
    url_parts = urlparse.urlsplit(args[0], 'http')
    url = urlparse.urlunsplit(url_parts[:-1] + ('',))

    # Path, including parameters (unique identifier within a host)
    path = urlparse.urlunsplit(('', '') + url_parts[2:-1] + ('',))

    # Host, without default port
    host = re.sub(r':80$', '', url_parts[1])

    # Fetch the requested URL
    res = urllib2.urlopen(url)
    data = res.read()

    store_dir = os.path.join(options.dir, host)
    # Create store directory if it doesn't already exist.
    if not os.access(store_dir, os.F_OK):
        os.makedirs(store_dir)
        
    print url
    print path
    print host
    print os.path.join(store_dir, md5.md5(path).hexdigest())
