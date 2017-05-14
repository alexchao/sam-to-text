# -*- coding: utf-8 -*-
import unittest

from sam_to_text import util


class FormatTimestamp(unittest.TestCase):

    def test_rounded_float(self):
        self.assertEqual(
            util.format_timestamp(15.9),
            '00:00:16')

    def test_single_digit_seconds(self):
        self.assertEqual(
            util.format_timestamp(9),
            '00:00:09')

    def test_seconds(self):
        self.assertEqual(
            util.format_timestamp(39),
            '00:00:39')

    def test_minutes(self):
        self.assertEqual(
            util.format_timestamp(542),
            '00:09:02')

    def test_hours(self):
        self.assertEqual(
            util.format_timestamp(3719),
            '01:01:59')


if __name__ == '__main__':
    unittest.main()
