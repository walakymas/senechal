import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# The database connection is opened lazily, so importing the data layer needs no database.

import winter_logic
from api import views
from api.compat import Request
from commands.winter import Winter
from database.charactertable import CharacterTable
from database.markstable import MarksTable
from permissions import NO_RIGHTS

def setUpModule():
    # Config.reload reads the yml files and a `hook` property from the database: no database here
    from config import Config
    from database.proptable import PropertiesTable
    with mock.patch.object(PropertiesTable, 'getValue', return_value=None):
        Config.reload()


UNCHECKED, FAILED, INCREASE, UPDATED = MarksTable.UNCHECKED, MarksTable.FAILED, MarksTable.INCREASE, MarksTable.UPDATED


def row(id, spec, status, year=481, dbid=5):
    # marks table columns: id, created, modified, year, lord, spec, dbid, status
    return (id, None, '2026-01-01', year, None, spec, dbid, status)


def raw_data():
    return {'name': 'Bors', 'skills': {'Combat': {'Sword': 15}, 'Other': {'Courtesy': 10}},
            'traits': {'cha': 10, 'ene': 10, 'for': 10, 'gen': 10, 'hon': 12, 'jus': 10, 'mer': 10, 'mod': 10,
                       'pru': 10, 'spi': 10, 'tem': 10, 'tru': 10, 'val': 10},
            'passions': {'Loyalty (lord)': 15},
            'stats': {'siz': 10, 'dex': 10, 'str': 10, 'con': 10, 'app': 10}}


class MarkStatusTest(unittest.TestCase):

    def test_roll_against_the_value(self):
        self.assertEqual(winter_logic.mark_status(10, 10), FAILED)
        self.assertEqual(winter_logic.mark_status(1, 10), FAILED)
        self.assertEqual(winter_logic.mark_status(11, 10), INCREASE)
        self.assertEqual(winter_logic.mark_status(20, 19), INCREASE)

    def test_over_20_only_a_natural_20_increases(self):
        self.assertEqual(winter_logic.mark_status(19, 25), FAILED)
        self.assertEqual(winter_logic.mark_status(20, 25), INCREASE)
        self.assertEqual(winter_logic.mark_status(20, 20), FAILED)


class ResolveMarkTest(unittest.TestCase):

    def test_exact_name_wins_over_a_prefix(self):
        data = raw_data()
        data['skills']['Other']['Sword Master'] = 3
        self.assertEqual(winter_logic.resolve_mark(data, 'Sword')[1:3], ['Sword', 15])

    def test_opposite_trait_and_passion_and_missing(self):
        data = raw_data()
        self.assertEqual(winter_logic.resolve_mark(data, 'Deceitful')[1:3], ['Deceitful', 8])
        self.assertEqual(winter_logic.resolve_mark(data, 'Loyalty (lord)')[1:3], ['Loyalty (lord)', 15])
        self.assertIsNone(winter_logic.resolve_mark(data, 'Nothing'))
        self.assertIsNone(winter_logic.resolve_mark(data, 'Size'))  # stats cannot be marked


class CheckMarksTest(unittest.TestCase):

    def run_check(self, rows, rolls, force=False):
        char = SimpleNamespace(id=5, get_data=raw_data)
        with mock.patch.object(MarksTable, 'list', return_value=rows), \
                mock.patch.object(MarksTable, 'set_status') as set_status, \
                mock.patch('utils.dice', side_effect=rolls) as dice:
            lines = winter_logic.check_marks(char, 481, force)
        return lines, set_status, dice

    def test_only_unchecked_marks_are_rolled(self):
        rows = [row(1, 'Sword', UNCHECKED), row(2, 'Courtesy', UNCHECKED), row(3, 'Honest', FAILED),
                row(4, 'Loyalty (lord)', INCREASE)]
        lines, set_status, dice = self.run_check(rows, [15, 3])
        self.assertEqual(dice.call_count, 2)
        self.assertEqual([c.args for c in set_status.call_args_list], [(1, FAILED), (2, FAILED)])
        self.assertIn('Honest', lines[2])
        self.assertIn('---', lines[2])
        self.assertIn('Increase', lines[3])
        self.assertIn('--', lines[3])

    def test_increase_is_stored(self):
        lines, set_status, _ = self.run_check([row(1, 'Courtesy', UNCHECKED)], [11])
        set_status.assert_called_once_with(1, INCREASE)
        self.assertIn('Increase', lines[0])

    def test_force_rolls_everything_but_updated(self):
        rows = [row(1, 'Sword', FAILED), row(2, 'Courtesy', INCREASE), row(3, 'Honest', UPDATED)]
        lines, set_status, dice = self.run_check(rows, [20, 1], force=True)
        self.assertEqual([c.args for c in set_status.call_args_list], [(1, INCREASE), (2, FAILED)])
        self.assertIn('Updated', lines[2])


class UpdateMarksTest(unittest.TestCase):

    def run_update(self, rows, data=None):
        data = data or raw_data()
        record = (5, None, None, None, 'Bors', None, json.dumps(data))
        with mock.patch.object(MarksTable, 'list', return_value=rows), \
                mock.patch.object(CharacterTable, 'get_by_id', return_value=record), \
                mock.patch.object(CharacterTable, 'set_json') as set_json, \
                mock.patch.object(MarksTable, 'set_status_many') as set_status, \
                mock.patch.object(winter_logic.Character, 'get_by_id'):
            changes = winter_logic.update_marks(5, 481)
        return changes, set_json, set_status

    def test_increase_marks_are_raised_by_one(self):
        rows = [row(1, 'Sword', INCREASE), row(2, 'Courtesy', FAILED), row(3, 'Loyalty (lord)', INCREASE),
                row(4, 'Honest', INCREASE)]
        changes, set_json, set_status = self.run_update(rows)
        self.assertEqual(changes, [('Sword', 15, 16), ('Loyalty (lord)', 15, 16), ('Honest', 12, 13)])
        saved = json.loads(set_json.call_args.args[1])
        self.assertEqual(saved['skills']['Combat']['Sword'], 16)
        self.assertEqual(saved['skills']['Other']['Courtesy'], 10)
        self.assertEqual(saved['passions']['Loyalty (lord)'], 16)
        self.assertEqual(saved['traits']['hon'], 13)
        set_status.assert_called_once_with([1, 3, 4], UPDATED)

    def test_opposite_trait_lowers_the_stored_value(self):
        changes, set_json, _ = self.run_update([row(1, 'Deceitful', INCREASE)])
        self.assertEqual(changes, [('Deceitful', 8, 9)])
        self.assertEqual(json.loads(set_json.call_args.args[1])['traits']['hon'], 11)

    def test_nothing_to_update(self):
        changes, set_json, set_status = self.run_update([row(1, 'Sword', FAILED), row(2, 'Courtesy', UPDATED)])
        self.assertEqual(changes, [])
        set_json.assert_not_called()
        set_status.assert_not_called()

    def test_unknown_marks_stay_increase(self):
        changes, set_json, set_status = self.run_update([row(1, 'Nothing', INCREASE)])
        self.assertEqual(changes, [])
        set_json.assert_not_called()


def make_message(content, did=42):
    message = MagicMock()
    message.author.id = did
    message.author.mention = '<@42>'
    message.channel.send = AsyncMock()
    message.content = content
    return message


class WinterCommandTest(unittest.IsolatedAsyncioTestCase):

    async def test_force_needs_admin(self):
        message = make_message('!winter force')
        with mock.patch('commands.winter.has_rights', return_value=False), \
                mock.patch('commands.winter.run_winter') as run:
            await Winter().handle(['force'], message, MagicMock())
        run.assert_not_called()
        message.channel.send.assert_awaited_once_with('<@42>' + NO_RIGHTS)

    async def test_admin_force_and_the_character_before_it(self):
        message = make_message('!winter !Bors force')
        char = SimpleNamespace(id=5)
        result = MagicMock()
        result.embed_fields.return_value = []
        with mock.patch('commands.winter.has_rights', return_value=True), \
                mock.patch('commands.winter.get_me', return_value=char) as get_me, \
                mock.patch('commands.winter.run_winter', return_value=result) as run, \
                mock.patch('commands.winter.send_embed_fields', new=AsyncMock()):
            await Winter().handle(['!Bors', 'force'], message, MagicMock())
        self.assertEqual(get_me.call_args.kwargs['words'], ['winter', '!Bors'])
        run.assert_called_once_with(char, True)

    async def test_without_force_nobody_is_checked_for_rights(self):
        message = make_message('!winter')
        char = SimpleNamespace(id=5)
        result = MagicMock()
        result.embed_fields.return_value = []
        with mock.patch('commands.winter.has_rights') as rights, \
                mock.patch('commands.winter.get_me', return_value=char), \
                mock.patch('commands.winter.run_winter', return_value=result) as run, \
                mock.patch('commands.winter.send_embed_fields', new=AsyncMock()):
            await Winter().handle([], message, MagicMock())
        rights.assert_not_called()
        run.assert_called_once_with(char, False)


PLAYER = (1, 555, None, 1, 0, 1, 'Player', 3)   # TokenTable.get_info_by_token: id, did, expires, tokenstate, rights, state, name, cid
OTHER = (2, 777, None, 1, 0, 1, 'Other', 4)
HOST = (3, 999, None, 1, 1, 1, 'Host', 6)


class WebApiTest(unittest.TestCase):

    def call(self, view, record, **post):
        from api import feast_views
        char = SimpleNamespace(id=5, name='Bors', memberid=555)
        with mock.patch.object(feast_views, 'session', return_value=record), \
                mock.patch.object(views.Character, 'get_by_id', return_value=char), \
                mock.patch.object(winter_logic.Character, 'get_by_id', return_value=char), \
                mock.patch.object(views, 'MarksTable') as table, \
                mock.patch('winter_logic.update_marks', return_value=[('Sword', 15, 16)]) as update, \
                mock.patch('winter_logic.run_winter') as run:
            table.year.return_value = 481
            table.return_value.list.return_value = []
            run.return_value = SimpleNamespace(year=481, text=lambda: 'report')
            response = view(Request(GET={}, POST=dict(id='5', **post)))
        return response, update, run

    def test_update_needs_the_owner_or_an_admin(self):
        response, update, _ = self.call(views.marks_update, None)
        self.assertEqual(response.status, 403)
        response, update, _ = self.call(views.marks_update, OTHER)
        self.assertEqual(response.status, 403)
        update.assert_not_called()
        for record in (PLAYER, HOST):
            response, update, _ = self.call(views.marks_update, record)
            self.assertEqual(response.status, 200)
            update.assert_called_once_with(5, 481)
            self.assertEqual(json.loads(response.content)['changes'], [{'name': 'Sword', 'old': 15, 'new': 16}])

    def test_winter_force_is_admin_only(self):
        response, _, run = self.call(views.winter, PLAYER, force='true')
        self.assertEqual(response.status, 403)
        run.assert_not_called()
        response, _, run = self.call(views.winter, HOST, force='true')
        self.assertEqual(response.status, 200)
        self.assertEqual(run.call_args.args[1], True)
        response, _, run = self.call(views.winter, PLAYER)
        self.assertEqual(response.status, 200)
        self.assertEqual(run.call_args.args[1], False)
        self.assertEqual(json.loads(response.content)['text'], 'report')

    def test_winter_of_a_foreign_character_is_refused(self):
        response, _, run = self.call(views.winter, OTHER)
        self.assertEqual(response.status, 403)
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
