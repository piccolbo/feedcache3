========================================================
 feedcache - Maintain a cache of RSS and Atom Feed Data
========================================================

This is a draft python3 only version of the original. Unfortunately a project 
has taken me in a different direction so I can't quite finish the job. 
It seems to be working, but there is a problem in the test_server that
prevents the extensive test suite from completing.

The feedcache package implements a class to wrap Mark Pilgrim's
Universal Feed Parser module so that parameters can be used to cache
the feed results locally instead of fetching the feed every time it is
requested. Uses both etag and modified times for caching. The cache is
parameterized to use different backend storage options.
