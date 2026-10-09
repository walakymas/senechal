import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# The database connection is opened lazily, so importing the data layer needs no database.

from api import feast_views, views as views_module
views = views_module
from api.compat import Request
import feast as feast_module

DID = 555          # the Discord id of the player of character 5
PLAYER = (1, DID, None, 1, 0, 1, 'Player', 3)       # TokenTable.get_info_by_token: id, did, expires, tokenstate, rights, state, name, cid
OTHER = (2, 777, None, 1, 0, 1, 'Other', 4)
HOST = (3, 999, None, 1, 1, 1, 'Host', 6)
EXPIRED = (4, DID, None, 1, 0, 0, 'Player', 3)


def guest(glory=0, position='near', **extra):
    g = {'position': position, 'glory': glory, 'state': 'init', 'rounds': {}, 'activeCards': [], 'tags': [],
         'significant': []}
    g.update(extra)
    return g


def feast_row(guests, state='feast', round=1, rounds=3):
    data = {'participiants': guests, 'state': state, 'round': round, 'rounds': rounds, 'course': {}}
    return (7, None, None, 'feast', 'desc', json.dumps(data), json.dumps({'deck': list(range(1, 30)), 'pos': -1}))


def character(cid=5, memberid=DID, app=10):
    return SimpleNamespace(id=cid, name=f'Char{cid}', memberid=memberid, data={'stats': {'app': app}},
                           get_data=lambda: {'stats': {'app': app}})


class FeastApiTest(unittest.TestCase):

    def setUp(self):
        self.tokens = {'player': PLAYER, 'other': OTHER, 'host': HOST, 'expired': EXPIRED}
        self.row = None
        for target in (feast_views, feast_module, views):
            p = mock.patch.object(target, 'FeastTable')
            table = p.start()
            self.addCleanup(p.stop)
            table.return_value.get.side_effect = lambda *a: self.row
        p = mock.patch.object(feast_views, 'TokenTable')
        tokens = p.start()
        self.addCleanup(p.stop)
        tokens.return_value.get_info_by_token.side_effect = lambda t: self.tokens.get(t)
        p = mock.patch.object(feast_views.Character, 'get_by_id', side_effect=lambda cid: {5: character(), 6: character(6, 999)}.get(int(cid)))
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(feast_views.EventsTable, 'glory', return_value=1500)
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(feast_module.Config, 'feast', return_value={'1': {'tags': ['host']}, '2': {}})
        p.start()
        self.addCleanup(p.stop)

    def call(self, view, token='player', **post):
        post = {k: str(v) for k, v in post.items()}
        if token:
            post['token'] = token
        response = view(Request(POST=post))
        return response.status, json.loads(response.content)

    def test_a_valid_session_is_needed(self):
        self.row = feast_row({'5': guest()})
        for token in (None, 'nope', 'expired'):
            status, body = self.call(feast_views.feast_activity, token, cid=5, activity='gossip')
            self.assertEqual(status, 403, token)

    def test_a_player_acts_only_for_his_own_character(self):
        self.row = feast_row({'5': guest()})
        self.assertEqual(self.call(feast_views.feast_activity, 'other', cid=5, activity='gossip')[0], 403)
        self.assertEqual(self.call(feast_views.feast_activity, 'player', cid=5, activity='gossip')[0], 200)
        self.row = feast_row({'5': guest(rounds={'1': {'action': 'gossip'}})})
        self.assertEqual(self.call(feast_views.feast_activity, 'host', cid=5, activity='flirt')[0], 409)  # already chosen

    def test_only_the_host_runs_the_feast(self):
        self.row = feast_row({'5': guest()}, state='init')
        self.assertEqual(self.call(feast_views.feast_next, 'player')[0], 403)
        status, body = self.call(feast_views.feast_next, 'host')
        self.assertEqual((status, body['data']['state'], body['data']['round']), (200, 'feast', 1))
        self.assertEqual(self.call(feast_views.feast_seat, 'player', cid=5, seat='above')[0], 403)

    def test_bad_parameters_are_400(self):
        self.row = feast_row({'5': guest()}, state='init')
        self.assertEqual(self.call(feast_views.feast_seat, 'host', cid='x', seat='near')[0], 400)
        self.assertEqual(self.call(feast_views.feast_seat, 'host', cid=5, seat='roof')[0], 400)
        self.assertEqual(self.call(feast_views.feast_get, None, fid='x')[0], 400)

    def test_no_feast_is_404_and_nothing_is_created(self):
        self.row = None
        self.assertEqual(self.call(feast_views.feast_get, None)[0], 404)
        self.assertEqual(views.feast(Request(GET={})).status, 404)

    def test_card_activity_is_refused_above_the_salt(self):
        self.row = feast_row({'5': guest(5000, 'above')})
        status, body = self.call(feast_views.feast_activity, 'player', cid=5, activity='card')
        self.assertEqual(status, 409)
        status, body = self.call(feast_views.feast_activity, 'player', cid=5, activity='gossip')
        self.assertEqual(status, 200)

    def test_cards_are_listed_as_enabled_and_one_can_be_played(self):
        self.row = feast_row({'5': guest(2000)})
        status, body = self.call(feast_views.feast_activity, 'player', cid=5, activity='card')
        self.assertEqual(status, 200)
        cards = body['data']['participiants']['5']['rounds']['1']['cards']
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards, [1, 2])
        self.assertEqual(body['data']['participiants']['5']['enabled'], [1])      # card 1 is a host card: it must be played

    def test_app_roll_seats_the_guest_once(self):
        self.row = feast_row({}, state='init')
        rolls = [{'result': 'success', 'roll': 9, 'total': 9, 'target': 10}]
        with mock.patch.object(feast_views, 'roll', side_effect=rolls):
            status, body = self.call(feast_views.feast_app_roll, 'player', cid=5)
        self.assertEqual(status, 200)
        seated = body['data']['participiants']['5']
        self.assertEqual((seated['position'], seated['glory'], seated['app']), ('near', 1500, 9))
        self.assertEqual(body['rolled']['position'], 'near')
        self.row = feast_row({'5': seated}, state='init')
        self.assertEqual(self.call(feast_views.feast_app_roll, 'player', cid=5)[0], 409)

    def test_a_fumbled_app_roll_is_rolled_again(self):
        self.row = feast_row({}, state='init')
        rolls = [{'result': 'fumble', 'roll': 20, 'total': 20, 'target': 10},
                 {'result': 'success', 'roll': 9, 'total': 9, 'target': 10}]
        with mock.patch.object(feast_views, 'roll', side_effect=rolls):
            status, body = self.call(feast_views.feast_app_roll, 'player', cid=5)
        self.assertEqual(body['data']['participiants']['5']['position'], 'below')
        self.assertTrue(body['data']['participiants']['5']['fumbled'])

    def test_select_card_needs_an_enabled_card(self):
        self.row = feast_row({'5': guest(2000, rounds={'1': {'action': 'card', 'cards': [1, 2]}})})
        self.assertEqual(self.call(feast_views.feast_select_card, 'player', cid=5, card=2)[0], 409)  # the host card is first
        status, body = self.call(feast_views.feast_select_card, 'player', cid=5, card=1)
        self.assertEqual(status, 200)
        self.assertEqual(body['data']['participiants']['5']['rounds']['1']['selected'], 1)

    def test_roll_records_the_result_and_geniality(self):
        self.row = feast_row({'5': guest(rounds={'1': {'action': 'flirt'}}, geniality=12)})
        with mock.patch.object(feast_views, 'checkable_value', return_value=10) as value, \
                mock.patch.object(feast_views, 'roll', return_value={'result': 'success', 'roll': 5, 'total': 5, 'target': 20}) as rolled:
            status, body = self.call(feast_views.feast_roll, 'player', cid=5)
        self.assertEqual(status, 200)
        rolled.assert_called_once_with(10, 10)                         # the Geniality modifier is capped at +10
        self.assertEqual(body['data']['participiants']['5']['geniality'], 13)

    def test_leaving_needs_the_first_round_for_a_voluntary_departure(self):
        self.row = feast_row({'5': guest(geniality=4)}, round=1)
        self.assertEqual(self.call(feast_views.feast_leave, 'player', cid=5, voluntary=1)[0], 409)
        status, body = self.call(feast_views.feast_leave, 'player', cid=5)
        self.assertEqual((status, body['data']['participiants']['5']['geniality']), (200, 0))

    def test_legacy_actions_need_the_right(self):
        self.row = feast_row({'5': guest()}, state='init')
        self.assertEqual(views.feast(Request(POST={'action': 'nextState'})).status, 403)
        self.assertEqual(views.feast(Request(POST={'action': 'nextState', 'token': 'other'})).status, 403)
        self.assertEqual(views.feast(Request(POST={'action': 'nextState', 'token': 'host'})).status, 200)
        self.row = feast_row({'5': guest()})
        self.assertEqual(views.feast(Request(POST={'action': 'roundAction', 'roundAction': 'gossip', 'pid': '5', 'token': 'player'})).status, 200)
        self.assertEqual(views.feast(Request(GET={})).status, 200)                # reading stays open


if __name__ == '__main__':
    unittest.main()
