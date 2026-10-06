import logging
import os
import sys
import time
import unittest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import message_handler
from api.compat import content_disposition
from character import Character
from database.base_table_handler import BaseTableHandler
from database.charactertable import CharacterTable
from database.proptable import PropertiesTable


class ContentDispositionTest(unittest.TestCase):

    def test_plain_name(self):
        self.assertEqual(content_disposition('Sir Arthur.pdf'), 'inline; filename="Sir Arthur.pdf"')

    def test_quotes_semicolons_and_line_breaks_cannot_break_the_header(self):
        header = content_disposition('Sir "Q";x\r\nSet-Cookie: a=b.pdf')
        self.assertNotIn('\r', header)
        self.assertNotIn('\n', header)
        self.assertEqual(header.split('; filename*=')[0], 'inline; filename="Sir _Q__x__Set-Cookie: a=b.pdf"')

    def test_accented_name_gets_an_rfc5987_filename(self):
        header = content_disposition('Sir Árpád Őrmester.pdf')
        self.assertIn('filename="Sir _rp_d _rmester.pdf"', header)
        self.assertIn("filename*=UTF-8''Sir%20%C3%81rp%C3%A1d%20%C5%90rmester.pdf", header)

    def test_empty_name(self):
        self.assertTrue(content_disposition('').startswith('inline; filename="download"'))


def character_record(cid, did=None):
    return (cid, None, None, None, f'Char{cid}', None, '{}', None, None, did)


class CharacterCacheTest(unittest.TestCase):

    def setUp(self):
        Character.cache = {}
        self.table = mock.patch.object(CharacterTable, 'get_by_memberid', return_value=None).start()
        self.by_id = mock.patch.object(CharacterTable, 'get_by_id', return_value=character_record(1)).start()
        self.by_ids = mock.patch.object(CharacterTable, 'get_by_ids').start()

        def init(this, record):
            this.id = record[0]
            this.name = record[4]

        mock.patch.object(Character, '__init__', init).start()
        self.addCleanup(mock.patch.stopall)
        self.addCleanup(lambda: setattr(Character, 'cache', {}))

    def test_unknown_user_is_looked_up_once_and_again_after_the_negative_ttl(self):
        for _ in range(5):
            self.assertIsNone(Character.get_by_memberid(42))
        self.assertEqual(self.table.call_count, 1)
        key = ('member', 42)
        value, expires = Character.cache[key]
        self.assertLessEqual(expires - time.monotonic(), Character.NEGATIVE_TTL)
        Character.cache[key] = (value, time.monotonic() - 1)  # expired
        Character.get_by_memberid(42)
        self.assertEqual(self.table.call_count, 2)

    def test_text_and_number_ids_share_an_entry(self):
        Character.get_by_memberid('123')
        Character.get_by_memberid(123)
        self.assertEqual(self.table.call_count, 1)
        Character.get_by_id('1')
        Character.get_by_id(1)
        self.assertEqual(self.by_id.call_count, 1)

    def test_force_bypasses_the_cache(self):
        Character.get_by_id(1)
        Character.get_by_id(1, force=True)
        self.assertEqual(self.by_id.call_count, 2)

    def test_found_characters_live_longer_than_missing_ones(self):
        Character.get_by_id(1)
        self.assertGreater(Character.cache[('id', 1)][1] - time.monotonic(), Character.NEGATIVE_TTL)

    def test_many_loads_only_the_missing_ones_with_one_query(self):
        Character.get_by_id(1)
        self.by_ids.return_value = {2: character_record(2), 3: character_record(3)}
        found = Character.get_many_by_id([1, '2', 3, 2])
        self.assertEqual(sorted(found), [1, 2, 3])
        self.by_ids.assert_called_once()
        self.assertEqual(sorted(self.by_ids.call_args.args[0]), [2, 3])
        Character.get_many_by_id([1, 2, 3])  # now everything is cached
        self.by_ids.assert_called_once()

    def test_many_remembers_characters_that_do_not_exist(self):
        self.by_ids.return_value = {}
        self.assertEqual(Character.get_many_by_id([7]), {})
        Character.get_many_by_id([7])
        self.by_ids.assert_called_once()


class YearCacheTest(unittest.TestCase):

    def setUp(self):
        BaseTableHandler.clear_year_cache()
        self.addCleanup(BaseTableHandler.clear_year_cache)

    def test_year_is_read_once(self):
        with mock.patch.object(BaseTableHandler, 'execute', return_value=('482',)) as execute:
            self.assertEqual(BaseTableHandler.year(), 482)
            self.assertEqual(BaseTableHandler.year(), 482)
        self.assertEqual(execute.call_count, 1)

    def test_writing_the_year_property_drops_the_cache(self):
        with mock.patch.object(BaseTableHandler, 'execute', return_value=('482',)) as execute:
            BaseTableHandler.year()
            PropertiesTable().set('year', '483')
            BaseTableHandler.year()
        self.assertEqual(execute.call_count, 3)  # read, write, read again

    def test_other_properties_keep_the_cache(self):
        with mock.patch.object(BaseTableHandler, 'execute', return_value=('482',)) as execute:
            BaseTableHandler.year()
            PropertiesTable().set('hook', 'x')
            BaseTableHandler.year()
        self.assertEqual(execute.call_count, 2)  # read, write

    def test_expiry(self):
        with mock.patch.object(BaseTableHandler, 'execute', return_value=('482',)) as execute:
            BaseTableHandler.year()
            BaseTableHandler._year_cache = (482, time.monotonic() - 1)
            BaseTableHandler.year()
        self.assertEqual(execute.call_count, 2)


class LoggingTest(unittest.IsolatedAsyncioTestCase):

    async def test_arguments_are_not_logged_at_info_level(self):
        message = MagicMock()
        message.author.name = 'someone'
        message.author.id = 1
        message.author.mention = '<@1>'
        message.channel.send = AsyncMock()
        with mock.patch('commands.db.has_rights', return_value=False), \
                self.assertLogs('message_handler', level='INFO') as logs:
            await message_handler.handle_command('db', ['set', 'prop', 'hook', 'https://secret.example/hook'],
                                                 message, MagicMock())
        text = '\n'.join(logs.output)
        self.assertIn('db', text)
        self.assertNotIn('secret.example', text)

    async def test_arguments_are_logged_at_debug_level(self):
        message = MagicMock()
        message.author.name = 'someone'
        message.author.id = 1
        message.author.mention = '<@1>'
        message.channel.send = AsyncMock()
        with mock.patch('commands.db.has_rights', return_value=False), \
                self.assertLogs('message_handler', level='DEBUG') as logs:
            await message_handler.handle_command('db', ['list', 'prop'], message, MagicMock())
        self.assertIn('list', '\n'.join(logs.output))


if __name__ == '__main__':
    unittest.main()
