# The Creole Crawler

import sys
import urlparse
import re
import os.path
import md5
import robotparser
import bz2
import urllib2

__author__ = "Filip Salomonsson"
__version__ = "0.1a"

class Crawler:
    """Web crawler."""

    USER_AGENT = "Creole/%s" % __version__

    def __init__(self, store=".store", throttle_delay=1):
        self.store = store
        self.throttle_delay = throttle_delay

    def fetch(self, base_url):
        """Start a crawl from the given base url."""
        # Clean up the URL (get rid of any fragment identifier)
        url_parts = urlparse.urlsplit(base_url, 'http')
        url = urlparse.urlunsplit(url_parts[:-1] + ('',))

        # Path, including parameters (unique identifier within a host)
        path = urlparse.urlunsplit(('', '') + url_parts[2:-1] + ('',))

        # Host, without default port
        host = re.sub(r':80$', '', url_parts[1])

        # Customize the user-agent header
        robotparser.URLopener.version =  self.USER_AGENT
        headers = {"User-Agent": self.USER_AGENT}

        # Fetch and parse robots.txt, if available
        rp = robotparser.RobotFileParser()
        rp.set_url("http://%s/robots.txt" % host)
        rp.read()

        store_dir = os.path.join(self.store, host)
        # Create store directory if it doesn't already exist.
        if not os.access(store_dir, os.F_OK):
            os.makedirs(store_dir)

        path_hash = md5.new(path).hexdigest()

        # Fetch the requested URL, if allowed (and not already fetched)
        if not rp.can_fetch(self.USER_AGENT, url):
            raise Exception("Not allowed by robots.txt")

        elif os.access(os.path.join(store_dir, path_hash+".bzip2"), os.F_OK):
            raise Exception("Already stored.")

        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)

        # Store the response
        #@@: might not be the same URL as was requested; doublecheck?
        filename = os.path.join(store_dir, path_hash)
        tmp_filename = filename + ".tmp"
        f = bz2.BZ2File(tmp_filename, 'w')
        f.writelines(response.readlines())
        f.close()
        os.rename(tmp_filename, filename + '.bzip2')

        # ..and headers...
        filename = filename + ".headers"
        tmp_filename = filename + "'.tmp"
        f = open(tmp_filename, 'w')
        for (key, value) in sorted(response.info().items()):
            f.write("%s: %s\n" % (key, value))
        f.close()
        os.rename(tmp_filename, filename)

        print >> sys.stderr, "Successfully stored %s" % (url,)
