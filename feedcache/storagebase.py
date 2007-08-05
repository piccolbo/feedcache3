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

"""Define the API which must be supported by a storage handler for the cache.

"""

__module_id__ = "$Id$"

#
# Import system modules
#


#
# Import local modules
#


#
# Module
#

class StorageBase:
    """Base class to define the API which must be supported by a
    storage handler for the cache.
    """

    def open(self):
        """Prepare the storage to be used.
        """
        return

    def close(self):
        """Commit changes to the storage and disconnect
        any open resources.
        """
        return

    def get(self, url):
        """Return a 2 part tuple containing the time.time() value for when the
        cache was updated with data for the URL, and the data.
        If there is no data for the URL, return (None, None).
        """
        raise NotImplementedError()

    def set(self, url, parsedFeed):
        """Store the value of the parsed feed for the
        specified URL, replacing any content previously
        stored for that URL.
        """
        raise NotImplementedError()

    def markUpdated(self, url):
        """Update the modified time for the cached data
        without changing the data itself.
        """
        old_time, existing_data = self.get(url)
        self.set(url, existing_data)
        return
