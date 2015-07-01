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

    def _do_test_parse_URI(self, uri, expected_address, expected_amount, expected_label, expected_message, expected_request_url):
        address, amount, label, message, request_url = parse_URI(uri)
        self.assertEqual(expected_address, address)
        self.assertEqual(expected_amount, amount)
        self.assertEqual(expected_label, label)
        self.assertEqual(expected_message, message)
        self.assertEqual(expected_request_url, request_url)

    def test_parse_URI_address(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', '', '', '', '')

    def test_parse_URI_only_address(self):
        self._do_test_parse_URI('fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', None, None, None, None)


    def test_parse_URI_address_label(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?label=electrum%20test', 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', '', 'electrum test', '', '')

    def test_parse_URI_address_message(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?message=electrum%20test', 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', '', '', 'electrum test', '')

    def test_parse_URI_address_amount(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?amount=0.03', 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 30000, '', '', '')

    def test_parse_URI_address_request_url(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?r=http://domain.tld/page?h%3D2a8628fc2fbe', 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', '', '', '', 'http://domain.tld/page?h=2a8628fc2fbe')

    def test_parse_URI_ignore_args(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?test=test', 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', '', '', '', '')

    def test_parse_URI_multiple_args(self):
        self._do_test_parse_URI('faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?amount=0.004&label=electrum-test&message=electrum%20test&test=none&r=http://domain.tld/page', 'fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3', 4000, 'electrum-test', 'electrum test', 'http://domain.tld/page')

    def test_parse_URI_no_address_request_url(self):
        self._do_test_parse_URI('faircoin:?r=http://domain.tld/page?h%3D2a8628fc2fbe', '', '', '', '', 'http://domain.tld/page?h=2a8628fc2fbe')

    def test_parse_URI_invalid_address(self):
        self.assertRaises(AssertionError, parse_URI, 'faircoin:invalidaddress')

    def test_parse_URI_invalid(self):
        self.assertRaises(AssertionError, parse_URI, 'notbitcoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3')

    def test_parse_URI_parameter_polution(self):
        self.assertRaises(Exception, parse_URI, 'faircoin:fairVs8iHyLzgHQrdxb9j6hR4WGpdDbKN3?amount=0.0003&label=test&amount=30.0')
    
    def test_format_satoshis_plain(self):
        result = format_satoshis_plain(1234654320)
        expected = "1234.65432"
        self.assertEqual(expected, result)


