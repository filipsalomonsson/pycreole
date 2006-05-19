# The Creole Crawler

import sys
import re
import os.path
import robotparser
import bz2
import urlparse
import urllib2
import urlnorm
from cStringIO import StringIO
from elementtidy import TidyHTMLTreeBuilder
from base64 import urlsafe_b64encode, urlsafe_b64decode

__author__ = "Filip Salomonsson"
__version__ = "0.1a"

XHTML_NS = "{http://www.w3.org/1999/xhtml}"

class Crawler:
    """Web crawler."""

    USER_AGENT = "Creole/%s" % __version__

    def __init__(self, store=".store", throttle_delay=1):
        self.store = store
        self.throttle_delay = throttle_delay
        self.history = set()

    def crawl(self, base_url):
        """Start a crawl from the given base URL."""
        # Reset the queue
        self.url_queue = [base_url]

        while len(self.url_queue) > 0:
            url = self.url_queue.pop()
            doc = self.retrieve(url)
            urls = self.extract_urls(doc, url)
            self.url_queue.extend(urls)

    def retrieve(self, url):
        """Retrieve a single URL."""
        # Clean up the URL (get rid of any fragment identifier)
        url_parts = urlparse.urlsplit(url, 'http')
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

        basename = urlsafe_b64encode(path)

        # Fetch the requested URL, if allowed (and not already fetched)
        if not rp.can_fetch(self.USER_AGENT, url):
            raise Exception("Not allowed by robots.txt")

        # First, try in the store
        try:
            filename = os.path.join(store_dir, basename + ".bzip2")
            self.history.add(url)
            return bz2.BZ2File(filename).read()
        except IOError:
            pass

        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        self.history.add(response.geturl())
        doc = response.read()

        # Store the response
        #@@: might not be the same URL as was requested; doublecheck?
        filename = os.path.join(store_dir, basename)
        tmp_filename = filename + ".tmp"
        f = bz2.BZ2File(tmp_filename, 'w')
        f.write(doc)
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

        return doc

    def extract_urls(self, doc, base_url):
        """Parses a document and returns URLS found in it."""
        tree = TidyHTMLTreeBuilder.parse(StringIO(doc))
        root = tree.getroot()

        base_url = urlnorm.norms(base_url)

        urls = set()
        for elem in root.findall(".//%sa" % XHTML_NS):
            href = elem.get("href")
            url = urlnorm.norms(urlparse.urljoin(base_url, href))
            if urlparse.urlsplit(url)[:2] == urlparse.urlsplit(base_url)[:2] \
                   and url not in self.history:
                urls.add(url)
        return urls
