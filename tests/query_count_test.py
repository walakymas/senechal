"""Counts the SQL statements of the hot endpoints; needs a real PostgreSQL (TEST_DATABASE_URL, WIPED first).
The legacy `characters.memberid` column is filled too, because `pdfs` still selects the team by it.

The counts must not grow with the number of characters (no N+1 queries). Set QUERY_REPORT=1 to print the numbers.

    set TEST_DATABASE_URL=postgresql://t:test@127.0.0.1:55432/t
    set QUERY_REPORT=1
    python -m unittest tests.query_count_test -v
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

URL = os.environ.get('TEST_DATABASE_URL')
REPORT = os.environ.get('QUERY_REPORT')


def character_json(name, level=0):
    return json.dumps({
        'name': name, 'role': 'Knight',
        'stats': {'siz': 12, 'dex': 11, 'str': 13, 'con': 12, 'app': 10},
        'traits': {k: 10 for k in ['cha', 'ene', 'for', 'gen', 'hon', 'jus', 'mer', 'mod', 'pru', 'spi', 'tem', 'tru', 'val']},
        'passions': {'Loyalty (Lord)': 15, 'Love (Family)': 12, 'Honor': 8},
        'skills': {'Other': {'Courtesy': 10 + level, 'Stewardship': 5}, 'Combat': {'Sword': 12}, 'Weapons': {}},
        'main': {'Age': 25, 'Culture': 'British Christian', 'Religion': 'British Christian'},
        'combat': {'weapon': 'Sword', 'shield': 'None', 'armor': 'Clothing', 'spec': []},
    })


@unittest.skipUnless(URL, 'TEST_DATABASE_URL is not set')
class QueryCountTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ['DATABASE_URL'] = URL
        from database.database import Database
        cls.Database = Database
        Database.reset()
        with Database.lock:
            conn = Database.get()
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA public CASCADE")
                cur.execute("CREATE SCHEMA public")
            conn.commit()
            Database.initiate()
        from config import Config
        Config.reload(True)

    @classmethod
    def tearDownClass(cls):
        cls.Database.reset()

    def seed(self, count):
        """`count` player characters (with events, marks and connections) plus `count` npcs."""
        from database.base_table_handler import BaseTableHandler as B
        from database.charactertable import CharacterTable
        B.execute("TRUNCATE characters, player, events, marks, c2c RESTART IDENTITY", commit=True)
        for i in range(count):
            CharacterTable().add(character_json(f'Sir Pc{i}', i))
            CharacterTable().add(character_json(f'Npc{i}', i))
        ids = [r[0] for r in B.execute("SELECT id FROM characters ORDER BY id", fetch='all')]
        pcs = ids[0::2]
        for n, cid in enumerate(pcs):
            B.execute("INSERT INTO player (did, name, character) VALUES (%s, %s, %s)", [1000 + n, f'player{n}', cid])
            B.execute("UPDATE characters SET player = (SELECT cid FROM player WHERE character = %s), memberid = %s WHERE id = %s", [cid, 1000 + n, cid])
            B.execute("INSERT INTO events (dbid, year, description, glory) VALUES (%s, 481, 'e', 10)", [cid])
            B.execute("INSERT INTO marks (dbid, year, spec) VALUES (%s, 481, 'Courtesy')", [cid])
        for b in ids[1:]:  # the first character is connected to everybody
            B.execute("INSERT INTO c2c (c0, c1, connection, comment) VALUES (%s, %s, 'friend', '')", [ids[0], b])
        return ids, pcs

    def count(self, label, call):
        from database.base_table_handler import BaseTableHandler
        from character import Character
        original = BaseTableHandler.execute
        Character.cache = {}
        BaseTableHandler.clear_year_cache()
        from api import views
        views._pdfs_cache.update(built=0.0, data=None)
        counter = {'n': 0}

        def counting(*args, **kwargs):
            counter['n'] += 1
            return original(*args, **kwargs)

        BaseTableHandler.execute = staticmethod(counting)
        try:
            call()
        finally:
            BaseTableHandler.execute = staticmethod(original)
        if REPORT:
            print(f"QUERIES {label}: {counter['n']}")
        return counter['n']

    def assertConstant(self, label, make_call):
        small = self.measure(3, label, make_call)
        large = self.measure(12, label, make_call)
        self.assertLessEqual(large, small, f"{label}: {small} queries for 3 characters, {large} for 12")

    def measure(self, count, label, make_call):
        ids, pcs = self.seed(count)
        return self.count(f"{label} ({count * 2} characters)", make_call(ids, pcs))

    def test_pcs(self):
        from api import views
        from api.compat import Request
        self.assertConstant('pcs', lambda ids, pcs: lambda: views.pcs(Request()))

    def test_list_and_names(self):
        from api import views
        from api.compat import Request
        self.assertConstant('list', lambda ids, pcs: lambda: views.list(Request()))
        self.assertConstant('json (names)', lambda ids, pcs: lambda: views.get_character(Request()))

    def test_one_character(self):
        from api import views
        from api.compat import Request
        self.assertConstant('json?id', lambda ids, pcs: lambda: views.get_character(Request(GET={'id': str(pcs[0])})))

    def test_connections(self):
        from api import views
        from api.compat import Request
        self.assertConstant('connections', lambda ids, pcs: lambda: views.connections(Request(GET={'cid': str(ids[0])})))

    def test_pdfs(self):
        from api import views
        from api.compat import Request
        self.assertConstant('pdfs', lambda ids, pcs: lambda: views.pdfs(Request()))

    def test_discord_lookups(self):
        from character import Character
        self.assertConstant('Character.pcs()', lambda ids, pcs: lambda: list(Character.pcs()))
        self.assertConstant('Character.npcs()', lambda ids, pcs: lambda: list(Character.npcs()))

    # --- the answers must stay what they were -------------------------------------------------------------

    def test_pdfs_zip_content_and_cache(self):
        import io
        import zipfile
        from api import views
        from api.compat import Request
        ids, pcs = self.seed(3)
        views._pdfs_cache.update(built=0.0, data=None)
        response = views.pdfs(Request())
        self.assertEqual(response.headers['Content-Type'], 'application/zip')
        self.assertIn('teampdf.zip', response.headers['Content-Disposition'])
        with zipfile.ZipFile(io.BytesIO(response.content.read())) as zf:
            self.assertEqual(sorted(zf.namelist()), ['Sir Pc0.pdf', 'Sir Pc1.pdf', 'Sir Pc2.pdf'])
            for name in zf.namelist():
                self.assertTrue(zf.read(name).startswith(b'%PDF'), name)
        # the second request within the cache time builds nothing
        queries = []
        from database.base_table_handler import BaseTableHandler
        original = BaseTableHandler.execute
        BaseTableHandler.execute = staticmethod(lambda *a, **k: queries.append(a) or original(*a, **k))
        try:
            views.pdfs(Request())
        finally:
            BaseTableHandler.execute = staticmethod(original)
        self.assertEqual(queries, [])

    def test_single_pdf(self):
        from api import views
        from api.compat import Request
        ids, pcs = self.seed(2)
        response = views.pdf(Request(GET={'id': str(pcs[0])}))
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.read().startswith(b'%PDF'))

    def test_connections_show_the_other_character_from_both_sides(self):
        import json
        from api import views
        from api.compat import Request
        from database.c2ctable import C2CTable
        ids, pcs = self.seed(2)
        a, b = ids[0], ids[1]
        from database.base_table_handler import BaseTableHandler
        BaseTableHandler.execute("TRUNCATE c2c", commit=True)
        C2CTable().add(str(a), str(b), 'friend', '')
        for me, other in ((a, b), (b, a)):
            rows = json.loads(views.connections(Request(GET={'cid': str(me)})).content)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['char']['dbid'], other)
            self.assertEqual(rows[0]['marks'], ['Courtesy'] if other in pcs else [])

    def test_list_keeps_its_shape(self):
        import json
        from api import views
        from api.compat import Request
        from database.charactertable import CharacterTable
        self.seed(3)
        expected = []
        for ch in CharacterTable().list():
            expected.append({'id': ch[0], 'modified': ch[2].isoformat(), 'name': ch[4], 'type': 'pc' if ch[9] else 'npc',
                             'role': ch[7], 'player': ch[8], 'url': ch[5], 'memberid': str(ch[9])})
        actual = json.loads(views.list(Request()).content)
        for row in actual:
            row['modified'] = row['modified'][:19]
        for row in expected:
            row['modified'] = row['modified'][:19]
        self.assertEqual(actual, expected)
        names = json.loads(views.get_character(Request()).content)
        self.assertEqual(names, {ch[4]: ch[0] for ch in CharacterTable().list()})

    def test_pcs_view_has_the_glory(self):
        import json
        from api import views
        from api.compat import Request
        self.seed(2)
        result = json.loads(views.pcs(Request()).content)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(c['Glory'] == 10 for c in result))
        self.assertTrue(all(c['memberId'] for c in result))

    def test_character_gets_its_player_from_the_record(self):
        from character import Character
        from database.playertable import PlayerTable
        ids, pcs = self.seed(2)
        from unittest import mock
        with mock.patch.object(PlayerTable, 'did_by_character', side_effect=AssertionError('extra query')):
            self.assertEqual(Character.get_by_id(pcs[0], force=True).memberid, 1000)
            self.assertIsNone(Character.get_by_id(ids[1], force=True).memberid)
            self.assertEqual(Character.get_by_memberid(1001, force=True).id, pcs[1])
            self.assertEqual(Character.get_by_name('Sir Pc1', force=True).memberid, 1001)
            self.assertEqual({c.name for c in Character.pcs()}, {'Sir Pc0', 'Sir Pc1'})

    def test_unknown_discord_user_is_looked_up_once(self):
        from character import Character
        ids, pcs = self.seed(2)

        def call():
            for _ in range(5):
                Character.get_by_memberid(424242)

        n = self.count('5x unknown member', call)
        self.assertLessEqual(n, 1)


if __name__ == '__main__':
    unittest.main()
