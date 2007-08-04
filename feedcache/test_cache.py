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

#
# Import system modules
#
import logging
import os
import tempfile
import unittest

#
# Import local modules
#
import cache
import memorystorage

#
# Module
#
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
                    )

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
</feed>
"""

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

if __name__ == '__main__':
    unittest.main()
