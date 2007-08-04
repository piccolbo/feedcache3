#!/usr/bin/env python
#
# Copyright 2007 Doug Hellmann.
#
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Doug
# Hellmann not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

"""Unittests for feedcache.cache

"""

__module_id__ = "$Id$"

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
                    )

#
# Import system modules
#
import os
import tempfile
import threading
import time
import unittest
import urllib

#
# Import local modules
#
import cache
import memorystorage
from test_server import TestHTTPServer, TestHTTPHandler

#
# Module
#

class CacheTest(unittest.TestCase):

    FEED_DATA = """<?xml version="1.0" encoding="utf-8"?>

<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en-us">
  <title>CacheTest test data</title>
  <link href="http://localhost/feedcache/" rel="alternate"></link>
  <link href="http://localhost/feedcache/atom/" rel="self"></link>
  <id>http://localhost/feedcache/</id>
  <updated>2006-10-14T11:00:36Z</updated>
  <entry>
    <title>single test entry</title>
    <link href="http://www.example.com/" rel="alternate"></link>
    <updated>2006-10-14T11:00:36Z</updated>
    <author>
      <name>author goes here</name>
      <email>authoremail@example.com</email>
    </author>
    <id>http://www.example.com/</id>
    <summary type="html">description goes here</summary>
    <link length="100" href="http://www.example.com/enclosure" type="text/html" rel="enclosure">
    </link>
  </entry>
</feed>"""

    def setUp(self):
        # Establish test data
        handle, self.tmp_file = tempfile.mkstemp('.xml')
        os.close(handle)
        f = open(self.tmp_file, 'wt')
        try:
            f.write(self.FEED_DATA)
        finally:
            f.close()

        self.storage = memorystorage.MemoryStorage()
        self.cache = cache.Cache(self.storage, userAgent='feedcache.test')
        return

    def tearDown(self):
        try:
            os.unlink(self.tmp_file)
        except AttributeError:
            pass
        return

    def testRetrieveNotInCache(self):
        feed_data = self.cache[self.tmp_file]
        self.failUnless(feed_data)
        self.failUnlessEqual(feed_data.feed.title, 'CacheTest test data')
        return

    def testRetrieveIsInCache(self):
        # First fetch
        feed_data = self.cache[self.tmp_file]

        # Second fetch
        feed_data2 = self.cache[self.tmp_file]

        # Since it is the in-memory storage, we should have the
        # exact same object.
        self.failUnless(feed_data is feed_data2)
        return

    def testExpireDataInCache(self):
        # First fetch
        feed_data = self.cache[self.tmp_file]

        # Change the timeout and sleep to move the clock
        self.cache.time_to_live = 0
        time.sleep(1)

        # Second fetch
        feed_data2 = self.cache[self.tmp_file]

        # Since we reparsed, the cache response should be different.
        self.failIf(feed_data is feed_data2)
        return

class SingleWriteMemoryStorage(memorystorage.MemoryStorage):
    """Only allow the cache value for a URL to be updated one time.
    """

    def set(self, url, parsedFeed):
        if url in self.data.keys():
            raise AssertionError('Trying to update cache for %s twice' % url)
        memorystorage.MemoryStorage.set(self, url, parsedFeed)
        return

    def markUpdated(self, url):
        """Update the modified time for the cached data
        without changing the data itself.
        """
        existing = self.getContent(url)
        self.data[url] = (time.time(), existing)
        return
    

class CacheServerTest(unittest.TestCase):

    def setUp(self):
        self.server = TestHTTPServer()
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True) # so the tests don't hang if cleanup fails
        self.server_thread.start()

        self.storage = SingleWriteMemoryStorage()
        self.cache = cache.Cache(self.storage,
                                 timeToLiveSeconds=0,
                                 userAgent='feedcache.test',
                                 )
        return

    def tearDown(self):
        # Stop the server thread
        ignore = urllib.urlretrieve('http://localhost:9999/shutdown')
        time.sleep(1)
        self.server.server_close()
        return

    def testFetchOnceForEtag(self):
        # First fetch populates the cache
        response1 = self.cache['http://localhost:9999/']
        self.failUnlessEqual(response1.feed.title, 'CacheTest test data')

        # Remove the modified setting from the cache so we know
        # the next time we check the etag will be used
        # to check for updates.  Since we are using an in-memory
        # cache, modifying response1 updates the cache storage
        # directly.
        response1['modified'] = None

        # Wait so the cache data times out
        time.sleep(1)

        # This should result in a 304 status, and no data from
        # the server.  That means the cache won't try to
        # update the storage, so our SingleWriteMemoryStorage
        # should not raise.
        response2 = self.cache['http://localhost:9999/']

        # Should have hit the server twice
        self.failUnlessEqual(self.server.getNumRequests(), 2)
        return

    def testFetchOnceForModifiedTime(self):
        # First fetch populates the cache
        response1 = self.cache['http://localhost:9999/']
        self.failUnlessEqual(response1.feed.title, 'CacheTest test data')

        # Remove the etag setting from the cache so we know
        # the next time we check the modified time will be used
        # to check for updates.  Since we are using an in-memory
        # cache, modifying response1 updates the cache storage
        # directly.
        response1['etag'] = None

        # Wait so the cache data times out
        time.sleep(1)

        # This should result in a 304 status, and no data from
        # the server.  That means the cache won't try to
        # update the storage, so our SingleWriteMemoryStorage
        # should not raise.
        response2 = self.cache['http://localhost:9999/']

        # Should have hit the server twice
        self.failUnlessEqual(self.server.getNumRequests(), 2)
        return


if __name__ == '__main__':
    unittest.main()
