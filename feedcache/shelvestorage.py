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

"""Cache storage using shelve for the backend.

"""

from __future__ import with_statement

__module_id__ = "$Id$"

#
# Import system modules
#
import os
import shelve
import threading
import time

#
# Import local modules
#
import storagebase

#
# Module
#

class ShelveStorage(storagebase.StorageBase):

    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.lock = threading.Lock()
        return

    def open(self):
        with self.lock:
            if self.data is not None:
                raise RuntimeError('ShelveStorage(%s) is already open' % self.filename)
            if os.path.exists(self.filename):
                flags = 'w'
            else:
                flags = 'c'
            self.data = shelve.open(self.filename, flags)
        return

    def close(self):
        with self.lock:
            if self.data is not None:
                self.data.close()
                self.data = None
        return

    def __del__(self):
        self.close()
        return

    def _mustBeOpened(self):
        if self.data is None:
            raise RuntimeError('ShelveStorage used without being opened.')

    def get(self, url):
        self._mustBeOpened()
        try:
            with self.lock:
                record = self.data[url]
        except KeyError:
            record = (None, None)
        return record

    def set(self, url, parsedFeed):
        self._mustBeOpened()
        with self.lock:
            record = (time.time(), parsedFeed)
            self.data[url] = record
        return
