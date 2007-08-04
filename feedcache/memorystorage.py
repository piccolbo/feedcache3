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

"""An in-memory implementation of the StorageBase API.

"""

__module_id__ = "$Id$"

#
# Import system modules
#
import time

#
# Import local modules
#
import storagebase

#
# Module
#

class MemoryStorage(storagebase.StorageBase):
    "An in-memory implementation of the StorageBase API."

    def __init__(self):
        self.data = {}

    def getAge(self, url):
        return self.data.get(url, (None, None))[0]

    def getContent(self, url):
        return self.data.get(url, (None, None))[1]

    def set(self, url, parsedFeed):
        self.data[url] = (time.time(), parsedFeed)
        return
