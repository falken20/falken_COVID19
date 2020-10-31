import unittest

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import falken_covid19


class TestFalkenCovid19(unittest.TestCase):

    def test_create_list_url(self):
        self.assertEqual(falken_covid19.create_list_urls(_month_from='13'), [])
        self.assertRaises(ValueError, falken_covid19.create_list_urls, 2020, 'd')

    def test_load_data_urls(self):
        self.assertEqual(falken_covid19.load_data_urls([], True), [])

    def test_generate_data_lists(self):
        self.assertEqual(falken_covid19.generate_data_lists([]), ([], [], []))
        self.assertRaises(TypeError, falken_covid19.generate_data_lists)


if __name__ == '__main__':
    unittest.main()
