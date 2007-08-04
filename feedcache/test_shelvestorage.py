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

"""Tests for the shelvestorage module.

"""

__module_id__ = "$Id$"

#
# Import system modules
#
import os
import shelve
import tempfile
import unittest

#
# Import local modules
#
import shelvestorage

#
# Module
#

class ShelveStorageTest(unittest.TestCase):

    def setUp(self):
        # Establish test data
        handle, self.shelve_file = tempfile.mkstemp('.shelve')
        os.close(handle)
        # Remove the file so it is recreated by the ShelveStorage
        try:
            os.unlink(self.shelve_file)
        except AttributeError:
            pass
        self.storage = shelvestorage.ShelveStorage(self.shelve_file)
        self.storage.open()
        return

    def tearDown(self):
        try:
            self.storage.close()
        except AttributeError:
            pass
        try:
            os.unlink(self.shelve_file)
        except AttributeError:
            pass
        return

    def testAddMissingDataToStorage(self):
        url = 'url_goes_here'
        data = { 'foo':'bar' }
        self.storage.set(url, data)
        self.storage.close()

        s = shelve.open(self.shelve_file)
        try:
            self.failUnless(url in s.keys())
            value = s[url]
        finally:
            s.close()

        self.failUnlessEqual(value[1], data)
        return

    def testRetrieveExistingData(self):
        url = 'url_goes_here'
        data = { 'foo':'bar' }
        self.storage.set(url, data)
        self.storage.close()

        storage = shelvestorage.ShelveStorage(self.shelve_file)
        storage.open()
        try:
            value = storage.getContent(url)
        finally:
            storage.close()

        self.failUnlessEqual(value, data)
        return

if __name__ == '__main__':
    unittest.main()
