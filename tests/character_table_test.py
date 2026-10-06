import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# The database connection is opened lazily, so importing the data layer needs no database.
if 'psycopg2' not in sys.modules:
    try:
        import psycopg2  # noqa: F401
    except ImportError:
        sys.modules['psycopg2'] = mock.MagicMock()

from database.base_table_handler import BaseTableHandler
from database.charactertable import CharacterTable


class GetByNameTest(unittest.TestCase):

    def test_name_is_a_parameter_not_part_of_the_sql(self):
        evil = "x'; DROP TABLE characters; --"
        with mock.patch.object(BaseTableHandler, 'execute', return_value=None) as execute:
            CharacterTable().get_by_name(evil)
        sql = execute.call_args.args[0]
        self.assertNotIn('DROP', sql)
        self.assertNotIn(evil, sql)
        self.assertEqual(execute.call_args.kwargs['param'], [f"%{evil}%"])

    def test_like_wildcards_match_literally(self):
        self.assertEqual(CharacterTable.like_pattern('50%_off'), '%50\\%\\_off%')
        self.assertEqual(CharacterTable.like_pattern('a\\b'), '%a\\\\b%')

    def test_plain_name_unchanged(self):
        self.assertEqual(CharacterTable.like_pattern('Arthur'), '%Arthur%')


if __name__ == '__main__':
    unittest.main()
