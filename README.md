Amazon Reviewers
================

Simple scraper to get the profiles of Amazon reviewers for a certain product.

Useful for finding those who may have given a good product a bad rating.

**NOTE**: Requires `bs4` and `lmxl` to work properly. Tests require the `mock`
module.


Usage
-----

    >>> inception_url = 'http://link-to-inception'
    >>> from amazon import Product
    >>> # Find people who gave Inception a 1-star review.
    ... Product(inception_url).reviewers(1)
    ['http://one-dumb-reviewer', 'http://second-dumb-reviewer', ...]


Amazon Terms of Service
-----------------------

This module is purely for educational purposes only.

If you plan on using it, be sure to thoroughly read [Amazon's Conditions of
Use](http://www.amazon.com/gp/help/customer/display.html/ref=cm_cd_help?ie=UTF8&nodeId=508088).


License
-------

**Author**: Zach Williams

All of my code is released under [the Unlicense](http://unlicense.org/) (a.k.a.
Public Domain).
