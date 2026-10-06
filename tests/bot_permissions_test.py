import os
import sys
import types
import unittest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# database.database connects to PostgreSQL on import; replace it with a stub.
_stub = types.ModuleType('database.database')
_stub.Database = MagicMock()
sys.modules.setdefault('database.database', _stub)

import message_handler
import permissions
from commands.db import Db
from database.playertable import PlayerTable
from dicing import roll_dice
from permissions import NO_RIGHTS
from utils import MAX_DICE_COUNT, MAX_DIE_SIZE


def make_message(did=42):
    message = MagicMock()
    message.author.id = did
    message.author.mention = '<@42>'
    message.author.send = AsyncMock()
    message.channel.send = AsyncMock()
    message.content = '!x'
    return message


class DiceLimitsTest(unittest.TestCase):

    def test_limits_are_accepted(self):
        text, _ = roll_dice(str(MAX_DICE_COUNT), str(MAX_DIE_SIZE))
        self.assertEqual(len(text.split('=')[0].split('+')), MAX_DICE_COUNT)
        roll_dice('', '6')  # '!d6'

    def test_too_many_dice(self):
        with self.assertRaises(ValueError):
            roll_dice(str(MAX_DICE_COUNT + 1), '6')
        with self.assertRaises(ValueError):
            roll_dice('999999999', '6')

    def test_bad_size(self):
        with self.assertRaises(ValueError):
            roll_dice('1', '0')
        with self.assertRaises(ValueError):
            roll_dice('1', str(MAX_DIE_SIZE + 1))


class HasRightsTest(unittest.TestCase):

    def check(self, rights, expected):
        with mock.patch.object(PlayerTable, 'rights', return_value=rights):
            self.assertEqual(permissions.has_rights(1), expected)

    def test_admin_bit(self):
        self.check(0, False)
        self.check(2, False)
        self.check(1, True)
        self.check(1023, True)


class CommandRightsTest(unittest.IsolatedAsyncioTestCase):

    async def test_protected_commands_are_refused_without_rights(self):
        for name in ('reload', 'set', 'info', 'images'):
            cmd = message_handler.COMMAND_ALIASES[name]
            message = make_message()
            args = ['k', 'v'] if name == 'set' else []
            with mock.patch.object(message_handler, 'has_rights', return_value=False), \
                    mock.patch.object(type(cmd), 'handle', new=AsyncMock()) as handle:
                await message_handler.handle_command(name, args, message, MagicMock())
            handle.assert_not_called()
            message.channel.send.assert_awaited_once_with('<@42>' + NO_RIGHTS)

    async def test_protected_command_runs_with_rights(self):
        cmd = message_handler.COMMAND_ALIASES['info']
        message = make_message()
        with mock.patch.object(message_handler, 'has_rights', return_value=True), \
                mock.patch.object(type(cmd), 'handle', new=AsyncMock()) as handle:
            await message_handler.handle_command('info', [], message, MagicMock())
        handle.assert_awaited_once()

    async def test_help_needs_no_rights(self):
        cmd = message_handler.COMMAND_ALIASES['reload']
        message = make_message()
        with mock.patch.object(message_handler, 'has_rights', return_value=False), \
                mock.patch.object(type(cmd), 'help', new=AsyncMock()) as help_:
            await message_handler.handle_command('reload', ['help'], message, MagicMock())
        help_.assert_awaited_once()

    async def test_unprotected_command_needs_no_rights(self):
        cmd = message_handler.COMMAND_ALIASES['mark']
        self.assertFalse(getattr(cmd, 'required_rights', 0))

    async def test_oversized_dice_message_is_refused(self):
        message = make_message()
        message.content = '!999999999d6'
        with mock.patch.object(message_handler, 'get_me', return_value=None):
            await message_handler.handle_command('999999999d6', [], message, MagicMock())
        message.channel.send.assert_awaited_once()
        self.assertIn('kockák száma', message.channel.send.await_args.args[0])


class DbCommandRightsTest(unittest.IsolatedAsyncioTestCase):

    async def test_prop_access_needs_admin(self):
        message = make_message()
        with mock.patch('commands.db.has_rights', return_value=False), \
                mock.patch('commands.db.PropertiesTable') as props:
            await Db().handle(['list', 'prop'], message, MagicMock())
            await Db().handle(['set', 'prop', 'hook', 'x'], message, MagicMock())
        props.assert_not_called()
        self.assertEqual(message.channel.send.await_count, 2)

    async def test_own_lord_data_stays_open(self):
        message = make_message()
        with mock.patch('commands.db.has_rights', return_value=False) as has_rights, \
                mock.patch('commands.db.get_me', return_value=None):
            await Db().handle(['set', 'lord', 'a', 'b'], message, MagicMock())
        has_rights.assert_not_called()
        message.channel.send.assert_not_called()
        message.author.send.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
