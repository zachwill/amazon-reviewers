#!/usr/bin/env python

"""
Find profiles for Amazon reviewers based on their review ratings for a certain
product.
"""

import re
from urllib2 import (Request, urlopen)
from urlparse import (urlsplit, urlunsplit)
from urllib import urlencode

from bs4 import BeautifulSoup as bs


class Product(object):
    """
    Find information about a product from it's Amazon link.

    >>> amazon_url = 'http://link-to-inception'
    >>> inception = Product(amazon_url)
    >>> all_reviewers = inception.reviewers()
    >>> one_star_reviewers = inception.reviewers(1)
    """

    def __init__(self, url):
        self.firefox = {
            'User-agent': ('Mozilla/5.0 (Macintosh; U; Intel Mac OS 10.5;'
                           ' en-US; rv:1.9) Gecko/2009122115 Firefox/3.0')
        }
        self.split_url = urlsplit(url)
        self.reviews_url = urlsplit(self._product_reviews_url(url))

    def _product_reviews_url(self, url):
        """
        Internal method to find the product reviews URL for an Amazon
        product.
        """
        temp_url = re.sub('/dp/', '/product-reviews/', url)
        return re.sub('ref=(.+)\?', 'cm_cr_pr_top_link_1', temp_url)

    def _star_reviews_url(self, star_num=None, page_num=1):
        """Internal method to return the star review URLs for a product."""
        star_params = {
            1: 'addOneStar',
            2: 'addTwoStar',
            3: 'addThreeStar',
            4: 'addFourStar',
            5: 'addFiveStar',
        }
        params = {
            'ie': 'UTF-8',
            'showViewPoints': 0,
            'pageNumber': page_num,
        }
        if star_num:
            params.update({'filterBy': star_params[star_num]})
        old_url = self.reviews_url
        star_reviews_url = (old_url.scheme, old_url.netloc, old_url.path,
                            urlencode(params), None)
        return urlunsplit(star_reviews_url)

    def _number_of_review_pages(self, star_num):
        """Find the number of review pages for a product."""
        url = self._star_reviews_url(star_num)
        content = urlopen(url).read()
        soup = bs(content, ['fast', 'lxml'])
        span = soup.find('span', 'paging')
        number_of_pages = span.findChildren('a')[1].contents[0]
        return int(number_of_pages)

    def _parse_reviewers(self, content):
        """
        Internal method to parse a review page with BeautifulSoup and return
        the links to profiles for Amazon reviewers.
        """
        soup = bs(content, ['fast', 'lxml'])
        table = soup.find('table', {'id': 'productReviews'})
        reviewers = [link['href'] for link in table.findAll('a')\
                        if link.contents == ['See all my reviews']]
        return reviewers

    def _star_reviewers(self, star_num, page_num):
        """Find reviewers based on number of stars given in review."""
        one_star_url = self._star_reviews_url(star_num, page_num)
        req = Request(one_star_url, headers=self.firefox)
        content = urlopen(req).read()
        return self._parse_reviewers(content)

    def reviewers(self, stars=None):
        """
        Find the profiles for reviewers -- based on the star rating they
        gave a specific product.

        >>> amazon_url = 'http://link-to-book'
        >>> book = Product(amazon_url)
        >>> one_star_reviews = book.reviewers(1)
        >>> five_star_reviews = book.reviewers(5)

        It's also possible to find the profiles of all reviewers for a product.

        >>> all_reviews = book.reviewers()
        """
        number_of_pages = self._number_of_review_pages(stars) + 1
        all_reviewers = []
        for page_num in xrange(1, number_of_pages):
            all_reviewers.extend(self._star_reviewers(stars, page_num))
        return all_reviewers
