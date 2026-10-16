import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api import views
from api.compat import Request


class ChecksViewTest(unittest.TestCase):

    def call(self, **get):
        with mock.patch.object(views, 'CheckTable') as table:
            table.return_value.list.return_value = []
            response = views.checks(Request(GET=get, POST={}))
        return response, table.return_value.list

    def test_default_is_the_last_10_of_everybody(self):
        response, listing = self.call()
        self.assertEqual(response.status, 200)
        listing.assert_called_once_with(plyr=None, limit=10)

    def test_limit_and_player(self):
        _, listing = self.call(limit='100', player='7')
        listing.assert_called_once_with(plyr=7, limit=100)

    def test_limit_is_clamped(self):
        _, listing = self.call(limit='5000')
        listing.assert_called_once_with(plyr=None, limit=100)
        _, listing = self.call(limit='0')
        listing.assert_called_once_with(plyr=None, limit=1)

    def test_bad_numbers_are_refused(self):
        for get in ({'limit': 'x'}, {'player': 'x'}):
            response, listing = self.call(**get)
            self.assertEqual(response.status, 400)
            listing.assert_not_called()


if __name__ == '__main__':
    unittest.main()
