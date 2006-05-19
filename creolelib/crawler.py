# The Creole Crawler

import sys
import re
import os.path
import time
import robotparser
import bz2
import urllib2
import urlnorm
from cStringIO import StringIO
from elementtidy import TidyHTMLTreeBuilder
from base64 import urlsafe_b64encode, urlsafe_b64decode
from urlparse import urlsplit, urlunsplit, urljoin

__author__ = "Filip Salomonsson"
__version__ = "0.1a"

XHTML_NS = "{http://www.w3.org/1999/xhtml}"

class DebugWriter:
    def __init__(self):
        self.file = sys.stderr
    def write(self, msg):
        self.file.write(msg)
    def __call__(self, msg):
        self.file.write(msg)
debug = DebugWriter()
    
def clean_url(url):
    (proto, host, path, params, frag) = urlsplit(urlnorm.norms(url))
    return urlunsplit((proto, host, path, params, ''))
    

class Crawler:
    """Web crawler."""

    USER_AGENT = "Creole/%s" % __version__
    robotparser.URLopener.version =  USER_AGENT
    
    def __init__(self, store=".store", throttle_delay=1):
        self.store = store
        self.throttle_delay = throttle_delay
        self.history = set()
        self.robotcache = {}
        self.lastvisit = {}

    def crawl(self, base_url):
        """Start a crawl from the given base URL."""
        # Reset the queue
        self.url_queue = [base_url]

        while len(self.url_queue) > 0:
            url = self.url_queue.pop()
            doc = self.retrieve(url)
            urls = self.extract_urls(doc, url)
            self.url_queue.extend(urls)
            print >> debug, "Added %s new urls to queue." % len(urls)

    def retrieve(self, url):
        """Retrieve a single URL."""
        
        # Clean up the URL (normalize it and get rid of any
        # fragment identifier)        
        url = clean_url(url)
        (proto, host, path, params, _) = urlsplit(url)
        print >> debug, "Retrieving %s" % url

        store_dir = os.path.join(self.store, host)
        # Create store directory if it doesn't already exist.
        if not os.access(store_dir, os.F_OK):
            os.makedirs(store_dir)

        basename = urlsafe_b64encode(path)

        try:
            # Use cached robots.txt...
            rp = self.robotcache[host]
        except KeyError:
            # ...fetch and parse it if it wasn't in the cache
            rp = robotparser.RobotFileParser()
            rp.set_url(urljoin(url, "/robots.txt"))
            print >> debug, "Fetching /robots.txt first."
            rp.read()
            self.robotcache[host] = rp

        # Fetch the requested URL, if allowed (and not already fetched)
        if not rp.can_fetch(self.USER_AGENT, url):
            raise Exception("Not allowed by robots.txt")

        # First, try in the store
        filename = os.path.join(store_dir, basename + ".bzip2")
        try:
            stored = bz2.BZ2File(filename).read()
            print >> debug, "..Already in store!"
            self.history.add(url)
            return stored
        except IOError:
            pass

        # Customize the user-agent header
        headers = {"User-Agent": self.USER_AGENT}

        # Set up the request
        request = urllib2.Request(url, headers=headers)

        # Honor the throttling delay
        delta = time.time() - self.lastvisit.get(host, 0)
        if delta < self.throttle_delay:
            print >> debug, "Going too fast; sleeping for %.1f seconds..." \
                  % (self.throttle_delay - delta) 
            time.sleep(self.throttle_delay - delta)
        response = urllib2.urlopen(request)
        self.lastvisit[host] = time.time()
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

        print >> debug, "..Successfully stored!"

        return doc

    def extract_urls(self, doc, base_url):
        """Parses a document and returns URLS found in it."""
        tree = TidyHTMLTreeBuilder.parse(StringIO(doc))
        root = tree.getroot()

        base_url = clean_url(base_url)

        urls = set()
        for elem in root.findall(".//%sa" % XHTML_NS):
            href = elem.get("href")
            url = clean_url((urljoin(base_url, href)))
            if urlsplit(url)[:2] == urlsplit(base_url)[:2] \
                   and url not in self.history \
                   and url not in self.url_queue:
                urls.add(url)
        return urls
