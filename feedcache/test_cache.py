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

class CacheTestBase(unittest.TestCase):
    "Base class for Cache tests"

    TEST_URL = 'http://localhost:9999/'

    CACHE_TTL = 0

    def setUp(self):
        self.server = self.getServer()
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True) # so the tests don't hang if cleanup fails
        self.server_thread.start()

        self.storage = self.getStorage()
        self.storage.open()
        self.cache = cache.Cache(self.storage,
                                 timeToLiveSeconds=self.CACHE_TTL,
                                 userAgent='feedcache.test',
                                 )
        return

    def getServer(self):
        "Return a web server for the test."
        return TestHTTPServer()

    def getStorage(self):
        "Return a cache storage for the test."
        return memorystorage.MemoryStorage()

    def tearDown(self):
        self.storage.close()
        # Stop the server thread
        ignore = urllib.urlretrieve('http://localhost:9999/shutdown')
        time.sleep(1)
        self.server.server_close()
        return


class CacheTest(CacheTestBase):

    CACHE_TTL = 30

    def getServer(self):
        "These tests do not want to use the ETag or If-Modified-Since headers"
        return TestHTTPServer(applyModifiedHeaders=False)

    def testRetrieveNotInCache(self):
        # Retrieve data not already in the cache.
        feed_data = self.cache[self.TEST_URL]
        self.failUnless(feed_data)
        self.failUnlessEqual(feed_data.feed.title, 'CacheTest test data')
        return

    def testRetrieveIsInCache(self):
        # Retrieve data which is alread in the cache,
        # and verify that the second copy is identitical
        # to the first.

        # First fetch
        feed_data = self.cache[self.TEST_URL]

        # Second fetch
        feed_data2 = self.cache[self.TEST_URL]

        # Since it is the in-memory storage, we should have the
        # exact same object.
        self.failUnless(feed_data is feed_data2)
        return

    def testExpireDataInCache(self):
        # Retrieve data which is in the cache but which
        # has expired and verify that the second copy
        # is different from the first.

        # First fetch
        feed_data = self.cache[self.TEST_URL]

        # Change the timeout and sleep to move the clock
        self.cache.time_to_live = 0
        time.sleep(1)

        # Second fetch
        feed_data2 = self.cache[self.TEST_URL]

        # Since we reparsed, the cache response should be different.
        self.failIf(feed_data is feed_data2)
        return



class SingleWriteMemoryStorage(memorystorage.MemoryStorage):
    """Cache storage which only allows the cache value 
    for a URL to be updated one time.
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
        old_time, existing_data = self.get(url)
        self.data[url] = (time.time(), existing_data)
        return
    

class CacheUpdateTest(CacheTestBase):

    def getStorage(self):
        return SingleWriteMemoryStorage()

    def testFetchOnceForEtag(self):
        # Fetch data which has a valid ETag value, and verify
        # that while we hit the server twice the response
        # codes cause us to use the same data.

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
        # should not raise and we should have the same
        # response object.
        response2 = self.cache['http://localhost:9999/']
        self.failUnless(response1 is response2)

        # Should have hit the server twice
        self.failUnlessEqual(self.server.getNumRequests(), 2)
        return

    def testFetchOnceForModifiedTime(self):
        # Fetch data which has a valid Last-Modified value, and verify
        # that while we hit the server twice the response
        # codes cause us to use the same data.

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
        # should not raise and we should have the same
        # response object.
        response2 = self.cache['http://localhost:9999/']
        self.failUnless(response1 is response2)

        # Should have hit the server twice
        self.failUnlessEqual(self.server.getNumRequests(), 2)
        return


if __name__ == '__main__':
    unittest.main()
