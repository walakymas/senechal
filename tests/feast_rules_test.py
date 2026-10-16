import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import feast as feast_module
import feast_rules as rules
from feast import Feast


class RulesTest(unittest.TestCase):

    def test_seat_from_app_result(self):
        self.assertEqual(rules.seat_from_app_result('critical'), 'above')
        self.assertEqual(rules.seat_from_app_result('success'), 'near')
        self.assertEqual(rules.seat_from_app_result('failure'), 'below')

    def test_fumble_goes_one_seat_down_from_the_second_roll(self):
        self.assertEqual(rules.seat_after_fumble('critical'), 'near')
        self.assertEqual(rules.seat_after_fumble('success'), 'below')
        self.assertEqual(rules.seat_after_fumble('failure'), 'floor')
        self.assertEqual(rules.seat_after_fumble('fumble'), 'floor')   # a second fumble counts as a failure

    def test_seat_geniality(self):
        self.assertEqual([rules.seat_geniality(s) for s in rules.SEATS], [2, 1, 0, -1])
        self.assertEqual(rules.seat_geniality('floor', fumbled=True), -2)

    def test_number_of_cards_starts_at_1000_glory_inclusive(self):
        self.assertEqual(rules.number_of_cards(999, 'near'), 0)
        self.assertEqual(rules.number_of_cards(1000, 'near'), 1)
        self.assertEqual(rules.number_of_cards(1999, 'near'), 1)
        self.assertEqual(rules.number_of_cards(2000, 'below'), 2)
        self.assertEqual(rules.number_of_cards(4000, 'below'), 3)
        self.assertEqual(rules.number_of_cards(8000, 'below'), 4)
        self.assertEqual(rules.number_of_cards(16000, 'below'), 5)
        self.assertEqual(rules.number_of_cards(32000, 'floor'), 6)
        self.assertEqual(rules.number_of_cards(32000, 'above'), 0)

    def test_activity_geniality(self):
        self.assertEqual([rules.activity_geniality(r) for r in rules.RESULTS], [2, 1, 0, -1])

    def test_significant_traits_and_passions(self):
        traits = {'cha': 3, 'tem': 17, 'mod': 10}
        passions = {'Hospitability': 16, 'Honor': 15}
        self.assertEqual(sorted(rules.significant_traits(traits, passions)), ['hospitability', 'lustful', 'temperate'])

    def test_first_round_requirement(self):
        self.assertEqual(rules.first_round_requirement(['indulgent', 'lustful']), {'indulge': 'temperate', 'flirt': 'chaste'})
        self.assertEqual(rules.first_round_requirement(['proud']), {})

    def test_app_bonus_and_geniality_modifier_are_capped(self):
        self.assertEqual(rules.app_bonus(8, 5), 10)
        self.assertEqual(rules.clamp_geniality_modifier(15), 10)
        self.assertEqual(rules.clamp_geniality_modifier(-15), -10)

    def test_leave_keeps_only_negative_geniality(self):
        self.assertEqual(rules.leave_geniality(7), 0)
        self.assertEqual(rules.leave_geniality(-3), -3)

    def test_final_glory(self):
        guests = {'1': {'geniality': 8, 'position': 'above'}, '2': {'geniality': 5, 'position': 'near'},
                  '3': {'geniality': -4, 'position': 'floor'}}
        self.assertEqual(rules.final_glory(guests), {'1': 80 + 100, '2': 5, '3': 0})
        self.assertEqual(rules.final_glory(guests, royal=True), {'1': 80 + 200, '2': 105, '3': 100})
        self.assertEqual(rules.final_glory({}), {})


def record(data):
    return (7, None, None, 'feast', 'desc', json.dumps(data), json.dumps({'deck': list(range(1, 30)), 'pos': -1}))


def guest(glory=0, position='near', **extra):
    g = {'position': position, 'glory': glory, 'state': 'init', 'rounds': {}, 'activeCards': [], 'tags': [],
         'significant': []}
    g.update(extra)
    return g


def feast_with(guests, state='feast', rounds=3, round=1):
    return Feast(record({'participiants': guests, 'state': state, 'round': round, 'rounds': rounds, 'course': {}}))


class FeastFlowTest(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch.object(feast_module, 'FeastTable')
        self.table = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(feast_module.Config, 'feast', return_value={
            '1': {'tags': ['host']}, '2': {'geniality': 1}, '3': {}, '4': {'tags': ['keep'], 'keep': {'geniality': 1, 'draw': False}}})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_old_records_get_the_new_fields(self):
        f = feast_with({'5': guest()})
        self.assertEqual(f.data['participiants']['5']['geniality'], 0)
        self.assertFalse(f.data['participiants']['5']['left'])
        self.assertFalse(f.data['royal'])

    def test_above_the_salt_and_the_poor_cannot_draw(self):
        f = feast_with({'1': guest(5000, 'above'), '2': guest(999), '3': guest(1000)})
        for cid in '123':
            f.set_round_action('card', int(cid))
        rounds = {cid: f.data['participiants'][cid]['rounds'] for cid in '123'}
        self.assertEqual(rounds['1'], {'1': {}})
        self.assertEqual(rounds['2'], {'1': {}})
        self.assertEqual(len(rounds['3']['1']['cards']), 1)

    def test_unknown_action_is_refused(self):
        f = feast_with({'1': guest(5000)})
        f.set_round_action('dance', 1)
        self.assertNotIn('action', f.data['participiants']['1']['rounds']['1'])

    def test_first_round_requirement_is_noted(self):
        f = feast_with({'1': guest(0, significant=['lustful'])})
        f.set_round_action('gossip', 1)
        self.assertEqual(f.data['participiants']['1']['rounds']['1']['requires'], ['chaste'])

    def test_activity_result_gives_geniality_once(self):
        f = feast_with({'1': guest()})
        f.set_round_action('flirt', 1)
        self.assertTrue(f.record_result(1, 'critical'))
        self.assertFalse(f.record_result(1, 'fumble'))
        self.assertEqual(f.data['participiants']['1']['geniality'], 2)

    def test_seat_by_app(self):
        f = feast_with({'1': guest(), '2': guest()}, state='init')
        self.assertEqual(f.seat_by_app(1, 'critical'), 'above')
        self.assertIsNone(f.seat_by_app(2, 'fumble'))                 # the second roll is missing
        self.assertEqual(f.seat_by_app(2, 'fumble', 'failure'), 'floor')
        self.assertTrue(f.data['participiants']['2']['fumbled'])

    def test_one_card_per_round_with_base_geniality(self):
        f = feast_with({'1': guest(2000)})
        f.data['participiants']['1']['rounds']['1'] = {'cards': [2, 3]}
        f.select_card(1, 2)
        f.select_card(1, 3)
        p = f.data['participiants']['1']
        self.assertEqual(p['rounds']['1']['selected'], 2)
        self.assertEqual(p['geniality'], 1)

    def test_kept_card_gives_geniality_and_blocks_drawing(self):
        f = feast_with({'1': guest(2000)})
        f.data['participiants']['1']['rounds']['1'] = {'cards': [4]}
        f.select_card(1, 4)
        self.assertEqual(f.data['participiants']['1']['kept'], [4])
        f.next_state()                                               # end of round 1: seat (near) +1, kept card +1
        self.assertEqual(f.data['participiants']['1']['geniality'], 2)
        f.set_round_action('card', 1)                                # round 2: cannot draw while keeping the card
        self.assertEqual(f.data['participiants']['1']['rounds']['2']['cards'], [])

    def test_leaving_drops_positive_geniality_and_stops_the_accrual(self):
        f = feast_with({'1': guest(geniality=6), '2': guest(geniality=-3)})
        f.leave(1, 'critical')
        f.leave(2)
        f.next_state()
        p = f.data['participiants']
        self.assertEqual((p['1']['geniality'], p['2']['geniality']), (0, -3))
        self.assertEqual(p['1']['award'], 10)

    def test_end_of_the_feast_awards_glory(self):
        f = feast_with({'1': guest(geniality=4, position='above'), '2': guest(geniality=2)}, rounds=1)
        f.next_state()                                               # last round ends: above +2, near +1
        self.assertEqual(f.data['state'], 'end')
        p = f.data['participiants']
        self.assertEqual(p['1']['finalGlory'], 6 * 10 + 100)
        self.assertEqual(p['2']['finalGlory'], 3)

    def test_failed_requirement_forces_the_activity_and_success_draws_the_cards(self):
        f = feast_with({'1': guest(2000, significant=['indulgent']), '2': guest(2000, significant=['indulgent'])})
        f.set_round_action('card', 1)
        f.set_round_action('card', 2)
        self.assertNotIn('cards', f.data['participiants']['1']['rounds']['1'])     # nothing is drawn before the roll
        self.assertEqual(f.data['participiants']['1']['rounds']['1']['requires'], ['temperate'])
        self.assertTrue(f.resolve_requirement(1, 'temperate', 'failure'))
        r1 = f.data['participiants']['1']['rounds']['1']
        self.assertEqual((r1['action'], r1['forced'], r1['requires']), ('indulge', True, []))
        self.assertTrue(f.resolve_requirement(2, 'temperate', 'success'))
        self.assertEqual(len(f.data['participiants']['2']['rounds']['1']['cards']), 2)
        self.assertFalse(f.resolve_requirement(2, 'temperate', 'success'))          # no such requirement any more

    def test_result_waits_for_the_requirement(self):
        f = feast_with({'1': guest(significant=['lustful'])})
        f.set_round_action('gossip', 1)
        self.assertFalse(f.record_result(1, 'success'))
        f.resolve_requirement(1, 'chaste', 'success')
        self.assertTrue(f.record_result(1, 'success'))

    def test_host_card_disables_the_other_cards(self):
        cards = {'1': {'tags': ['host']}, '2': {}, '7': {'mandatory': 'lustful'}}
        with mock.patch.object(feast_module.Config, 'feast', return_value=cards):
            self.assertFalse(Feast.card_enabled(7, {'cards': [1, 7]}, ['lustful']))
            self.assertFalse(Feast.card_enabled(2, {'cards': [1, 2]}, []))
            self.assertTrue(Feast.card_enabled(1, {'cards': [1, 2]}, []))

    def test_unplayed_cards_are_discarded_at_the_end_of_the_round(self):
        f = feast_with({'1': guest(2000)})
        f.data['participiants']['1']['rounds']['1'] = {'cards': [2, 3], 'selected': 2}
        f.next_state()
        self.assertEqual(f.data['participiants']['1']['rounds']['1']['discarded'], [3])


if __name__ == '__main__':
    unittest.main()
