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

"""

"""

__module_id__ = "$Id$"

#
# Import system modules
#
import feedparser

import logging
import time

#
# Import local modules
#


#
# Module
#

logger = logging.getLogger('feedcache.cache')

class Cache:
    """A class to wrap Mark Pilgrim's FeedParser module so that parameters
    can be used to cache the feed results locally instead of fetching
    the feed every time it is requested. Uses both etag and modified
    times for caching.
    """

    def __init__(self, storage, timeToLiveSeconds=300, userAgent='feedcache'):
        """
        Arguments:

          storage -- Backing store for the cache.  It should follow
          the dictionary API, with URLs used as keys.  It should
          persist data.

          timeToLiveSeconds=300 -- The length of time content should
          live in the cache before an update is attempted.

          userAgent='feedcache' -- User agent string to be used when
          fetching feed contents.

        """
        self.storage = storage
        self.time_to_live = timeToLiveSeconds
        self.user_agent = userAgent
        return

    def __getitem__(self, url):
        "Return the feed at url."
        logger.debug('url="%s"' % url)

        modified = None
        etag = None

        # Does the storage contain a version of the data
        # which is not too old and does not have an error?
        cached_time = self.storage.getAge(url)
        if cached_time is not None:
            cached_content = self.storage.getContent(url)
            now = time.time()
            age = now - cached_time
            if age <= self.time_to_live:
                logger.debug('cached contents still valid')
                return cached_content
            
            # The cache is out of date, but we have
            # something.  Try to use the etag and modified_time
            # values from the cached content.
            etag = cached_content.get('etag')
            modified = cached_content.get('modified')
            logger.debug('cached etag=%s' % etag)
            logger.debug('cached modified=%s' % str(modified))

        # We know we need to fetch, so go ahead and do it.
        logger.debug('fetching...')
        parsed_result = feedparser.parse(url,
                                         agent=self.user_agent,
                                         modified=modified,
                                         etag=etag,
                                         )

        status = parsed_result.get('status', None)
        logger.debug('status=%s' % status)
        if status == 304:
            # No new data, based on the etag or modified values.
            # We need to update the modified time in the
            # storage, though, so we know that what we have
            # stored is up to date.
            self.storage.markUpdated(url)

        # There is new content, so store it unless there was an error.
        if not parsed_result.get('bozo_exception'):
            self.storage.set(url, parsed_result)

        return parsed_result

