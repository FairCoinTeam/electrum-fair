import unittest
from lib.util import format_satoshis, parse_URI, format_satoshis_plain

class TestUtil(unittest.TestCase):

    def test_format_satoshis(self):
        result = format_satoshis(1234)
        expected = "0.001234"
        self.assertEqual(expected, result)

    def test_format_satoshis_diff_positive(self):
        result = format_satoshis(1234, is_diff=True)
        expected = "+0.001234"
        self.assertEqual(expected, result)

    def test_format_satoshis_diff_negative(self):
        result = format_satoshis(-1234, is_diff=True)
        expected = "-0.001234"
        self.assertEqual(expected, result)

    def _do_test_parse_URI(self, uri, expected):
        result = parse_URI(uri)
        self.assertEqual(expected, result)

    def test_parse_URI_address(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3',
                                {'address': 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3'})

    def test_parse_URI_only_address(self):
        self._do_test_parse_URI('fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3',
                                {'address': 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3'})


    def test_parse_URI_address_label(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?label=electrum%20test',
                                {'address': 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 'label': 'electrum test'})

    def test_parse_URI_address_message(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?message=electrum%20test',
                                {'address': 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 'message': 'electrum test', 'memo': 'electrum test'})

    def test_parse_URI_address_amount(self):
        self._do_test_parse_URI('faircoin:15mKKb2eos1hWa6tisdPwwDC1a5J1y9nma?amount=0.0003',
                                {'address': '15mKKb2eos1hWa6tisdPwwDC1a5J1y9nma', 'amount': 30000})

    def test_parse_URI_address_request_url(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?r=http://domain.tld/page?h%3D2a8628fc2fbe',
                                {'address': 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 'r': 'http://domain.tld/page?h=2a8628fc2fbe'})

    def test_parse_URI_ignore_args(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?test=test',
                                {'address': 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 'test': 'test'})

    def test_parse_URI_multiple_args(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?amount=0.00004&label=electrum-test&message=electrum%20test&test=none&r=http://domain.tld/page',
                                {'address': 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 'amount': 4000, 'label': 'electrum-test', 'message': u'electrum test', 'memo': u'electrum test', 'r': 'http://domain.tld/page', 'test': 'none'})

    def test_parse_URI_no_address_request_url(self):
        self._do_test_parse_URI('faircoin:?r=http://domain.tld/page?h%3D2a8628fc2fbe',
                                {'r': 'http://domain.tld/page?h=2a8628fc2fbe'})

    def test_parse_URI_invalid_address(self):
        self.assertRaises(AssertionError, parse_URI, 'faircoin:invalidaddress')

    def test_parse_URI_invalid(self):
        self.assertRaises(AssertionError, parse_URI, 'notfaircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3')

    def test_parse_URI_parameter_polution(self):
        self.assertRaises(Exception, parse_URI, 'faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?amount=0.0003&label=test&amount=30.0')

