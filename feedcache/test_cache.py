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
logger = logging.getLogger('feedcache.test_cache')

#
# Import system modules
#
import os
import time
import unittest
import UserDict

#
# Import local modules
#
import cache
from test_server import HTTPTestBase, TestHTTPServer

#
# Module
#

class CacheTestBase(HTTPTestBase):

    def setUp(self):
        HTTPTestBase.setUp(self)

        self.storage = self.getStorage()
        self.cache = cache.Cache(self.storage,
                                 timeToLiveSeconds=self.CACHE_TTL,
                                 userAgent='feedcache.test',
                                 )
        return

    def getStorage(self):
        "Return a cache storage for the test."
        return {}

class CacheTest(CacheTestBase):

    CACHE_TTL = 30

    def getServer(self):
        "These tests do not want to use the ETag or If-Modified-Since headers"
        return TestHTTPServer(applyModifiedHeaders=False)

    def testRetrieveNotInCache(self):
        # Retrieve data not already in the cache.
        feed_data = self.cache.fetch(self.TEST_URL)
        self.failUnless(feed_data)
        self.failUnlessEqual(feed_data.feed.title, 'CacheTest test data')
        return

    def testRetrieveIsInCache(self):
        # Retrieve data which is alread in the cache,
        # and verify that the second copy is identitical
        # to the first.

        # First fetch
        feed_data = self.cache.fetch(self.TEST_URL)

        # Second fetch
        feed_data2 = self.cache.fetch(self.TEST_URL)

        # Since it is the in-memory storage, we should have the
        # exact same object.
        self.failUnless(feed_data is feed_data2)
        return

    def testExpireDataInCache(self):
        # Retrieve data which is in the cache but which
        # has expired and verify that the second copy
        # is different from the first.

        # First fetch
        feed_data = self.cache.fetch(self.TEST_URL)

        # Change the timeout and sleep to move the clock
        self.cache.time_to_live = 0
        time.sleep(1)

        # Second fetch
        feed_data2 = self.cache.fetch(self.TEST_URL)

        # Since we reparsed, the cache response should be different.
        self.failIf(feed_data is feed_data2)
        return



class SingleWriteMemoryStorage(UserDict.UserDict):
    """Cache storage which only allows the cache value 
    for a URL to be updated one time.
    """

    def __setitem__(self, url, data):
        if url in self.keys():
            modified, existing = self[url]
            # Allow the modified time to change, 
            # but not the feed content.
            if data[1] != existing:
                raise AssertionError('Trying to update cache for %s to %s' \
                                         % (url, data))
        UserDict.UserDict.__setitem__(self, url, data)
        return
    

class CacheConditionalGETTest(CacheTestBase):

    def getStorage(self):
        return SingleWriteMemoryStorage()

    def testFetchOnceForEtag(self):
        # Fetch data which has a valid ETag value, and verify
        # that while we hit the server twice the response
        # codes cause us to use the same data.

        # First fetch populates the cache
        response1 = self.cache.fetch(self.TEST_URL)
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
        response2 = self.cache.fetch(self.TEST_URL)
        self.failUnless(response1 is response2)

        # Should have hit the server twice
        self.failUnlessEqual(self.server.getNumRequests(), 2)
        return

    def testFetchOnceForModifiedTime(self):
        # Fetch data which has a valid Last-Modified value, and verify
        # that while we hit the server twice the response
        # codes cause us to use the same data.

        # First fetch populates the cache
        response1 = self.cache.fetch(self.TEST_URL)
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
        response2 = self.cache.fetch(self.TEST_URL)
        self.failUnless(response1 is response2)

        # Should have hit the server twice
        self.failUnlessEqual(self.server.getNumRequests(), 2)
        return


if __name__ == '__main__':
    unittest.main()
