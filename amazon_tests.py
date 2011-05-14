#!/usr/bin/env python

"""Tests for the `amazon.py` module."""

import unittest
from urlparse import (urlsplit, parse_qs)
from mock import Mock

import amazon
from amazon import Product
from strings_for_testing import (eleven_pages, five_pages, reviewers_table)


def set_up(cls):
    amazon.urlopen = Mock()
    cls.url = ('http://www.amazon.com/Inception-Two-Disc/dp/B002ZG981E'
               '/ref=cm_pr_product_top')


class TestProductInitialization(unittest.TestCase):

    def setUp(self):
        set_up(self)

    def test_empty_intialization_fails(self):
        self.assertRaises(TypeError, Product)

    def test_initialization_with_fake_url(self):
        movie =  Product(self.url)
        self.assertEqual(
            movie.split_url.path, ('/Inception-Two-Disc/dp/B002ZG981E/'
                                   'ref=cm_pr_product_top'))
        self.assertEqual(
            movie.reviews_url.path, ('/Inception-Two-Disc/product-reviews/'
                                     'B002ZG981E/ref=cm_pr_product_top'))

class TestStarReviewsUrl(unittest.TestCase):

    def test_star_reviews_url_for_1_star(self):
        url = 'http://www.amazon.com/inception/dp/ref=blah'
        star_review_url = Product(url)._star_reviews_url(1)
        expected_url = ('http://www.amazon.com/inception/product-reviews/'
                        'ref=blah?pageNumber=1&ie=UTF-8&filterBy=addOneStar'
                        '&showViewPoints=0')
        self.assertEqual(star_review_url, expected_url)

    def test_star_reviews_url_for_5_stars_and_page_number(self):
        url = 'http://www.amazon.com/inception/dp/ref=blah'
        star_review_url = Product(url)._star_reviews_url(5, 5)
        expected_url = ('http://www.amazon.com/inception/product-reviews/'
                        'ref=blah?pageNumber=5&ie=UTF-8&filterBy=addFiveStar'
                        '&showViewPoints=0')
        self.assertEqual(star_review_url, expected_url)


class TestNumberOfReviewPages(unittest.TestCase):

    def setUp(self):
        set_up(self)

    def test_number_of_pages_on_html_string_eleven_pages(self):
        amazon.urlopen().read = Mock(return_value=eleven_pages)
        number = Product(self.url)._number_of_review_pages(1)
        self.assertEqual(number, 11)

    def test_number_of_pages_on_html_string_five_pages(self):
        amazon.urlopen().read = Mock(return_value=five_pages)
        number = Product(self.url)._number_of_review_pages(1)
        self.assertEqual(number, 5)


class TestParseReviewers(unittest.TestCase):

    def test_parse_reviewers_for_html_string(self):
        expected_output = ['http://data-you-want', 'http://data-you-want',
                           'http://data-you-want']
        data = Product('http://fake')._parse_reviewers(reviewers_table)
        self.assertEqual(data, expected_output)


class TestStarReviewers(unittest.TestCase):

    def setUp(self):
        set_up(self)
        amazon.Request = Mock()
        amazon.urlopen().read = Mock(return_value=reviewers_table)

    def test_star_reviewers_for_1_star_5_page(self):
        Product('http://fake')._star_reviewers(1, 5)
        called_url = urlsplit(amazon.Request.call_args[0][0])
        parsed_query =  parse_qs(called_url.query)
        assert 'addOneStar' in parsed_query['filterBy']
        assert '5' in parsed_query['pageNumber']

    def test_star_reviewers_for_3_star_2_page(self):
        Product('http://fake')._star_reviewers(3, 2)
        called_url = urlsplit(amazon.Request.call_args[0][0])
        parsed_query =  parse_qs(called_url.query)
        assert 'addThreeStar' in parsed_query['filterBy']
        assert '2' in parsed_query['pageNumber']


class TestProductReviews(unittest.TestCase):

    def setUp(self):
        set_up(self)
        amazon.Request = Mock()
        amazon.urlopen().read = Mock(return_value=reviewers_table)
        product = Product('http://fake')
        product._number_of_review_pages = Mock(return_value=2)
        self.product = product

    def test_product_reviews_for_1_star(self):
        data = self.product.reviewers(1)
        expected_output = ['http://data-you-want', 'http://data-you-want',
                           'http://data-you-want', 'http://data-you-want',
                           'http://data-you-want', 'http://data-you-want']
        self.assertEqual(data, expected_output)

    def test_product_reviews_for_no_stars(self):
        data = self.product.reviewers()
        expected_output = ['http://data-you-want', 'http://data-you-want',
                           'http://data-you-want', 'http://data-you-want',
                           'http://data-you-want', 'http://data-you-want']
        self.assertEqual(data, expected_output)


if __name__ == '__main__':
    unittest.main()
