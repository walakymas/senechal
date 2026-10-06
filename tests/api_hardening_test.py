import os
import sys
import unittest
from unittest import mock
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# The database connection is opened lazily, so importing the data layer needs no database.

from api import app, views
from api.compat import Request


class CorsOriginsTest(unittest.TestCase):

    def test_default_list_has_no_sandbox_or_lan_origin(self):
        origins = app.cors_origins('')
        self.assertEqual(origins, set(app.DEFAULT_CORS_ORIGINS))
        for risky in ('https://codepen.io', 'https://cdpn.io', 'http://192.168.1.131'):
            self.assertNotIn(risky, origins)
        self.assertIn('http://localhost:4200', origins)

    def test_env_value_replaces_the_list(self):
        origins = app.cors_origins(' https://a.example.org/ ,https://b.example.org,, ')
        self.assertEqual(origins, {'https://a.example.org', 'https://b.example.org'})

    def test_env_var_is_used(self):
        with mock.patch.dict(os.environ, {'CORS_ORIGINS': 'https://only.example.org'}):
            self.assertEqual(app.cors_origins(), {'https://only.example.org'})
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('CORS_ORIGINS', None)
            self.assertEqual(app.cors_origins(), set(app.DEFAULT_CORS_ORIGINS))


class MapUrlTest(unittest.TestCase):

    def test_only_http_urls(self):
        for good in ('https://senechalweb.duckdns.org/attachments/1/a.png', 'http://example.org/x.jpg'):
            self.assertTrue(views.is_http_url(good), good)
        for bad in ('javascript:alert(1)', 'data:text/html,<script>', 'file:///etc/passwd', '//example.org/x',
                    'example.org/x.png', 'https://', '', None):
            self.assertFalse(views.is_http_url(bad), bad)

    def test_add_and_update_refuse_a_bad_url_without_touching_the_table(self):
        with mock.patch.object(views, 'MapsTable') as table:
            for handler, post in ((views.add_map, {'url': 'javascript:alert(1)'}),
                                  (views.update_map, {'id': '1', 'url': 'javascript:alert(1)'})):
                response = handler(Request(GET={}, POST=post))
                self.assertEqual(response.status, 400)
            table.assert_not_called()

    def test_add_map_stores_a_good_url(self):
        with mock.patch.object(views, 'MapsTable') as table, mock.patch.object(views, 'maps', return_value='ok'):
            views.add_map(Request(GET={}, POST={'url': 'https://example.org/a.png', 'name': 'a'}))
        table.return_value.add.assert_called_once_with('https://example.org/a.png', '', 0, 'a')


if __name__ == '__main__':
    unittest.main()
