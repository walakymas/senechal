import json
import os
import sys
import unittest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# The database connection is opened lazily, so importing the data layer needs no database.

import feast as feast_module
import message_handler
import utils
from character import Character
from commands.db import Db
from commands.weapon import Weapon
from database.charactertable import CharacterTable
from feast import Feast


# --- check2: a skill above 20 --------------------------------------------------

class Check2Test(unittest.TestCase):
    """Owner's rule: above 20 the check always succeeds, the excess is added to the roll and a total of
    20 or more is a critical success (+4d6 damage)."""

    def check(self, base, roll, modifier=0):
        with mock.patch.object(utils, 'dice', return_value=roll):
            return utils.check2(base, modifier, False)

    def test_skill_above_20_always_succeeds(self):
        for roll in range(1, 20):
            self.assertIn(self.check(25, roll)[4], (1, 2), roll)

    def test_modifier_above_20_counts_too(self):
        self.assertEqual(self.check(15, 3, 10)[4], 1)

    def test_excess_is_added_to_the_roll(self):
        (color, text, r, ro, success) = self.check(25, 14)
        self.assertEqual((r, ro, success), (19, 14, 1))

    def test_sum_of_20_or_more_is_critical(self):
        self.assertEqual(self.check(25, 15)[4], 2)   # 15 + 5 = 20
        self.assertEqual(self.check(25, 18)[4], 2)   # 23
        self.assertEqual(self.check(25, 20)[4], 2)   # a natural 20 is no fumble above 20

    def test_normal_skill(self):
        self.assertEqual(self.check(12, 12)[4], 2)   # exactly the skill: critical
        self.assertEqual(self.check(12, 5)[4], 1)
        self.assertEqual(self.check(12, 15)[4], 4)   # fail
        self.assertEqual(self.check(12, 20)[4], 3)   # fumble


# --- Weapon.embed -----------------------------------------------------------------

def make_character(armor_red=2, shield_red=1, con=10, siz=10):
    data = {'name': 'Sir Test', 'stats': {'str': 10, 'siz': siz, 'con': con},
            'combat': {'spec': []}}
    character = MagicMock()
    character.get_data.return_value = data
    character.armor = {'red': armor_red}
    character.shield = {'red': shield_red}
    return character


class WeaponTest(unittest.IsolatedAsyncioTestCase):

    async def run_embed(self, checks, odamage=-1, character=None, damage=-1, dice_value=3):
        ctx = MagicMock()
        ctx.send = AsyncMock()
        dice_calls = []

        def fake_dice(size):
            dice_calls.append(size)
            return dice_value

        # the knocked-down dexterity check calls check() once more
        with mock.patch('commands.weapon.check', side_effect=list(checks) + [(0, 'Success', 5, 1)] * 3), \
                mock.patch('commands.weapon.dice', side_effect=fake_dice), \
                mock.patch('commands.weapon.get_checkable', return_value=[['skill', 'Dex', 10]]):
            await Weapon.embed(ctx, character or make_character(), {'damage': damage, 'fumble': 'dropped'},
                               'Sword', 10, 0, 10, odamage)
        return ctx.send.await_args.kwargs['embed'].description, dice_calls

    async def test_opponent_wins_without_opponent_damage_does_not_crash(self):
        # the character fumbles, the opponent succeeds, and no opponent damage dice were given
        text, _ = await self.run_embed([(0, 'Fumble', 20, 3), (0, 'Success', 10, 1)])
        self.assertIn('Opponent won', text)
        self.assertNotIn('wound', text)

    async def test_wound_is_the_opponent_damage_minus_the_armor(self):
        # the character fails, the opponent succeeds and rolls 2d6 = 6; the armor reduces by 2
        text, _ = await self.run_embed([(0, 'Fail', 15, 4), (0, 'Success', 10, 1)], odamage=2)
        self.assertIn('reduction 2, wound: 4', text)

    async def test_partial_success_uses_shield_and_armor(self):
        text, _ = await self.run_embed([(0, 'Success', 8, 1), (0, 'Success', 12, 1)], odamage=2)
        self.assertIn('reduction 3, wound: 3', text)

    async def test_major_wound_and_knocked_down(self):
        character = make_character(armor_red=0, shield_red=0, con=2, siz=2)
        text, _ = await self.run_embed([(0, 'Fail', 15, 4), (0, 'Success', 10, 1)], odamage=2, character=character)
        self.assertIn('Major Wound', text)
        self.assertIn('Knocked down', text)

    async def test_critical_adds_four_dice(self):
        _, dice_calls = await self.run_embed([(0, 'Fail', 15, 4), (0, 'Critical', 10, 2)], odamage=2)
        self.assertEqual(len(dice_calls), 6)

    async def test_own_critical_adds_four_dice(self):
        _, dice_calls = await self.run_embed([(0, 'Critical', 10, 2), (0, 'Fail', 15, 4)], damage=2)
        self.assertEqual(len(dice_calls), 6)


# --- Feast ---------------------------------------------------------------------------

def feast_record(data):
    return (7, None, None, 'feast', 'desc', json.dumps(data), json.dumps({'deck': [1, 2, 3], 'pos': -1}))


def participant(glory=0):
    return {'position': 'near', 'glory': glory, 'state': 'init', 'rounds': {}, 'activeCards': [],
            'tags': [], 'significant': []}


class FeastTest(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch.object(feast_module, 'FeastTable')
        self.table = patcher.start()
        self.addCleanup(patcher.stop)

    def test_new_feast_gets_the_id_of_the_inserted_row(self):
        self.table.return_value.insert.return_value = 42
        self.assertEqual(Feast(None).id, 42)

    def test_round_action_is_set_once_even_after_the_data_was_reloaded(self):
        data = {'participiants': {'5': participant()}, 'state': 'feast', 'round': 1, 'rounds': 3, 'course': {}}
        first = Feast(feast_record(data))
        first.set_round_action('pass', 5)
        reloaded = Feast(feast_record(json.loads(json.dumps(first.data))))  # keys are strings after the JSON round trip
        reloaded.set_round_action('card', 5)
        self.assertEqual(reloaded.data['participiants']['5']['rounds'], {'1': {'action': 'pass'}})

    def test_set_action_and_select_card_use_the_current_round(self):
        data = {'participiants': {'5': participant()}, 'state': 'feast', 'round': 2, 'rounds': 3, 'course': {}}
        f = Feast(feast_record(data))
        f.set_action = None
        f.setAction(5, 'card')
        self.assertEqual(f.data['participiants']['5']['rounds']['2']['action'], 'card')
        f.data['participiants']['5']['rounds']['2']['cards'] = [10]
        with mock.patch.object(feast_module.Config, 'feast', return_value={'10': {}}):
            f.select_card(5, 10)
        self.assertEqual(f.data['participiants']['5']['rounds']['2']['selected'], 10)

    def test_add_participant_of_an_unknown_character_is_ignored(self):
        data = {'participiants': {}, 'state': 'init', 'round': 0, 'rounds': 3, 'course': {}}
        f = Feast(feast_record(data))
        with mock.patch.object(feast_module.Character, 'get_by_id', return_value=None):
            f.add_participiant(99)
        self.assertEqual(f.data['participiants'], {})

    def test_card_enabled(self):
        cards = {'1': {'tags': ['host']}, '2': {}, '3': {}, '7': {'mandatory': 'lustful'}}
        with mock.patch.object(feast_module.Config, 'feast', return_value=cards):
            enabled = Feast.card_enabled
            self.assertFalse(enabled(2, {'cards': [3]}))                           # not drawn
            self.assertFalse(enabled(2, {}))                                       # nothing drawn
            self.assertTrue(enabled(2, {'cards': [2, 3]}, []))                     # plain card
            self.assertTrue(enabled(1, {'cards': [1, 7]}, ['lustful']))            # host card
            self.assertTrue(enabled(7, {'cards': [2, 7]}, ['lustful']))            # mandatory for me
            self.assertFalse(enabled(2, {'cards': [2, 7]}, ['lustful']))           # another card is mandatory for me
            self.assertTrue(enabled(2, {'cards': [2, 7]}, ['chaste']))             # mandatory for somebody else


# --- parsing --------------------------------------------------------------------------

def message(content, author_id=1):
    m = MagicMock()
    m.content = content
    m.author.id = author_id
    return m


class GetMeTest(unittest.TestCase):

    def setUp(self):
        self.by_member = mock.patch.object(Character, 'get_by_memberid', return_value=None).start()
        self.by_name = mock.patch.object(Character, 'get_by_name', return_value=None).start()
        self.by_id = mock.patch.object(Character, 'get_by_id', return_value=None).start()
        self.addCleanup(mock.patch.stopall)

    def test_mention_forms(self):
        utils.get_me(message('!c str <@!123>'))
        self.by_member.assert_any_call('123', force=False)
        utils.get_me(message('!c str <@456>'))
        self.by_member.assert_any_call('456', force=False)

    def test_named_character_needs_a_name(self):
        utils.get_me(message('!c str !Arthur'))
        self.by_name.assert_called_once_with('Arthur', force=False)
        self.by_name.reset_mock()
        utils.get_me(message('!c str !'))  # a lone exclamation mark is not a name
        self.by_name.assert_not_called()

    def test_cid(self):
        utils.get_me(message('!c str cid:5'))
        self.by_id.assert_called_once_with(5, force=False)
        self.by_id.reset_mock()
        utils.get_me(message('!c str cid:abc'))  # used to raise ValueError
        self.by_id.assert_not_called()

    def test_empty_command_falls_back_to_the_author(self):
        utils.get_me(message('!   ', author_id=77))
        self.by_member.assert_called_with(77, force=False)

    def test_role_mention_is_not_looked_up(self):
        utils.get_me(message('!c str <@&123>', author_id=77))
        self.by_member.assert_called_once_with(77, force=False)

    def test_strip_mention(self):
        self.assertEqual(utils.strip_mention(['c', 'str', '<@!1>']), ['c', 'str'])
        self.assertEqual(utils.strip_mention(['c', 'str', '<@1>']), ['c', 'str'])
        self.assertEqual(utils.strip_mention(['c', '<@&1>']), ['c', '<@&1>'])
        self.assertEqual(utils.strip_mention([]), [])


class PcsTest(unittest.TestCase):

    def test_pcs_filters_by_name(self):
        rows = [(1, 0, 0, 0, 'Sir Arthur'), (2, 0, 0, 0, 'Sir Kay'), (3, 0, 0, 0, 'Sir Bedivere')]

        def init(self, record):
            self.name = record[4]

        with mock.patch.object(CharacterTable, 'get_pcs', return_value=rows), \
                mock.patch.object(Character, '__init__', init):
            names = lambda name: [c.name for c in Character.pcs(name)]
            self.assertEqual(names('kay'), ['Sir Kay'])
            self.assertEqual(names('sir'), ['Sir Arthur', 'Sir Kay', 'Sir Bedivere'])
            self.assertEqual(names(None), ['Sir Arthur', 'Sir Kay', 'Sir Bedivere'])
            self.assertEqual(names('*'), ['Sir Arthur', 'Sir Kay', 'Sir Bedivere'])
            self.assertEqual(names('nobody'), [])


class AliasTest(unittest.TestCase):

    def test_no_command_alias_is_shared(self):
        seen = {}
        for command in message_handler.COMMAND_HANDLERS.values():
            for alias in command.aliases or []:
                self.assertNotIn(alias, seen, f"{alias}: {command.name} and {seen.get(alias)}")
                self.assertNotIn(alias, message_handler.COMMAND_HANDLERS, f"{alias} is also a command name")
                seen[alias] = command.name

    def test_l_is_feast_and_tel_is_winter(self):
        self.assertEqual(message_handler.COMMAND_ALIASES['l'].name, 'feast')
        self.assertEqual(message_handler.COMMAND_ALIASES['tel'].name, 'winter')
        self.assertEqual(message_handler.COMMAND_ALIASES['lord'].name, 'lord')
        self.assertEqual(message_handler.COMMAND_ALIASES['token'].name, 'token')


class HandlerErrorsTest(unittest.IsolatedAsyncioTestCase):

    async def test_a_missing_parameter_is_reported_to_the_user(self):
        m = message('!mark remove')
        m.author.mention = '<@1>'
        m.channel.send = AsyncMock()
        cmd = message_handler.COMMAND_ALIASES['mark']
        with mock.patch.object(type(cmd), 'handle', new=AsyncMock(side_effect=IndexError)):
            await message_handler.handle_command('mark', ['remove'], m, MagicMock())
        self.assertIn('Hibás vagy hiányzó paraméter', m.channel.send.await_args.args[0])

    async def test_db_with_too_few_parameters(self):
        m = message('!db set prop')
        m.author.send = AsyncMock()
        m.channel.send = AsyncMock()
        with mock.patch('commands.db.has_rights', return_value=True), \
                mock.patch('commands.db.PropertiesTable') as props:
            await Db().handle(['set', 'prop'], m, MagicMock())
        props.assert_not_called()
        m.author.send.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
