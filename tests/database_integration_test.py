"""Runs against a real PostgreSQL; skipped unless TEST_DATABASE_URL is set. The database is WIPED first.

    docker run -d --rm --name senechal-test-pg -e POSTGRES_PASSWORD=test -e POSTGRES_USER=t -e POSTGRES_DB=t \
        -p 127.0.0.1:55432:5432 postgres:14
    set TEST_DATABASE_URL=postgresql://t:test@127.0.0.1:55432/t
    python -m unittest tests.database_integration_test
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

URL = os.environ.get('TEST_DATABASE_URL')


@unittest.skipUnless(URL, 'TEST_DATABASE_URL is not set')
class DatabaseIntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ['DATABASE_URL'] = URL
        import psycopg2
        from database.database import Database
        cls.Database = Database
        cls.psycopg2 = psycopg2
        Database.reset()
        with Database.lock:
            conn = Database.get()
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA public CASCADE")
                cur.execute("CREATE SCHEMA public")
            conn.commit()
            Database.initiate()

    @classmethod
    def tearDownClass(cls):
        cls.Database.reset()

    def scalar(self, sql, param=None):
        from database.base_table_handler import BaseTableHandler
        return BaseTableHandler.execute(sql, param, fetch='one')[0]

    # --- schema -------------------------------------------------------------

    def test_fresh_install_reaches_the_latest_version(self):
        self.assertEqual(self.scalar("SELECT value FROM properties WHERE key='dbversion'"), '18')
        for table in ('events', 'lord', 'marks', 'characters', 'tokens', 'player', 'checks', 'p2c', 'c2c', 'feast', 'maps'):
            self.assertTrue(self.scalar("SELECT to_regclass(%s) IS NOT NULL", [table]), table)

    def test_initiate_is_idempotent(self):
        with self.Database.lock:
            self.Database.initiate()
        self.assertEqual(self.scalar("SELECT value FROM properties WHERE key='dbversion'"), '18')

    def test_upgrade_from_17_collapses_duplicates(self):
        from database.base_table_handler import BaseTableHandler as B
        B.execute("DROP INDEX idx_c2c_c0_c1", commit=True)
        B.execute("DROP INDEX idx_p2c_player_character", commit=True)
        B.execute("UPDATE properties SET value='17' WHERE key='dbversion'", commit=True)
        for comment in ('old', 'new'):
            B.execute("INSERT INTO c2c (c0, c1, connection, comment) VALUES (7, 8, 'x', %s)", [comment])
            B.execute("INSERT INTO p2c (player, character, connection, comment) VALUES (7, 8, 'x', %s)", [comment])
        with self.Database.lock:
            self.Database.initiate()
        self.assertEqual(self.scalar("SELECT count(*) FROM c2c WHERE c0=7 AND c1=8"), 1)
        self.assertEqual(self.scalar("SELECT comment FROM c2c WHERE c0=7 AND c1=8"), 'new')
        self.assertEqual(self.scalar("SELECT count(*) FROM p2c WHERE player=7 AND character=8"), 1)

    def test_failed_migration_rolls_back(self):
        from database.base_table_handler import BaseTableHandler as B
        B.execute("UPDATE properties SET value='17' WHERE key='dbversion'", commit=True)
        B.execute("ALTER TABLE c2c RENAME TO c2c_gone", commit=True)  # step 17 -> 18 now fails
        try:
            with self.Database.lock:
                with self.assertRaises(self.psycopg2.Error):
                    self.Database.initiate()
            self.assertEqual(self.scalar("SELECT value FROM properties WHERE key='dbversion'"), '17')
        finally:
            B.execute("ALTER TABLE c2c_gone RENAME TO c2c", commit=True)
            with self.Database.lock:
                self.Database.initiate()

    # --- error handling and reconnect --------------------------------------

    def test_errors_are_raised_and_the_connection_stays_usable(self):
        from database.base_table_handler import BaseTableHandler as B
        with self.assertRaises(self.psycopg2.Error):
            B.execute("SELECT * FROM no_such_table", fetch='all')
        self.assertEqual(self.scalar("SELECT 1"), 1)

    def test_reconnects_after_the_server_dropped_the_connection(self):
        from database.base_table_handler import BaseTableHandler as B
        B.execute("SELECT 1", fetch='one')
        pid = self.Database.get().get_backend_pid()
        old_ping = self.Database.IDLE_PING_SECONDS
        self.Database.IDLE_PING_SECONDS = -1  # ping before every use
        try:
            other = self.psycopg2.connect(URL)
            other.autocommit = True
            with other.cursor() as cur:
                cur.execute("SELECT pg_terminate_backend(%s)", (pid,))
            other.close()
            self.assertEqual(self.scalar("SELECT 1"), 1)
            self.assertNotEqual(self.Database.get().get_backend_pid(), pid)
        finally:
            self.Database.IDLE_PING_SECONDS = old_ping

    # --- the table handlers whose SQL used to be invalid --------------------

    def test_lord_table(self):
        from database.lordtable import LordTable
        t = LordTable()
        t.set(5, 0, 'k', 'v')
        self.assertEqual(t.get(5, 0, 'k')[5], 'v')
        self.assertEqual(len(t.get_by_value(0, 'k', 'v')), 1)
        t.remove(5, 0, 'k')
        self.assertIsNone(t.get(5, 0, 'k'))

    def test_marks_table(self):
        from database.markstable import MarksTable
        MarksTable().set(1, 481, 'Sword')
        self.assertEqual(len(MarksTable().get(1, 481)), 1)

    def test_c2c_and_p2c_upsert(self):
        from database.c2ctable import C2CTable
        from database.p2ctable import P2CTable
        C2CTable().add('11', '12', 'friend', 'a')
        C2CTable().add('11', '12', 'enemy', 'b')
        self.assertEqual(C2CTable().get(11, 12)[5], 'enemy')
        self.assertEqual(len(C2CTable().list(11)), 1)
        P2CTable().add(11, 12, 'x', 'a')
        P2CTable().add(11, 12, 'y', 'b')
        self.assertEqual(P2CTable().get(11, 12)[5], 'y')
        P2CTable().remove(11, 12)
        self.assertIsNone(P2CTable().get(11, 12))

    def test_tokens_player_feast_properties(self):
        from database.base_table_handler import BaseTableHandler as B
        from database.feasttable import FeastTable
        from database.playertable import PlayerTable
        from database.proptable import PropertiesTable
        from database.tokenstable import TokenTable

        self.assertIsNone(PropertiesTable().getValue('missing'))

        B.execute("INSERT INTO player (cid, did, name) VALUES (900, 901, 'p')", commit=True)
        TokenTable().issue('tok1', 900)
        self.assertEqual(TokenTable().get('tok1')[4], 900)
        TokenTable().remove('tok1')
        self.assertIsNone(TokenTable().get('tok1'))
        PlayerTable().remove(900)
        self.assertIsNone(PlayerTable().get(900))

        B.execute("INSERT INTO feast (cid, title, description) VALUES (950, 't', 'd')", commit=True)

        class F:
            id, title, description = 950, 'new', 'desc'

        FeastTable().update(F)
        self.assertEqual(FeastTable().get(950)[4], 'desc')
        FeastTable().remove(950)
        self.assertIsNone(FeastTable().get(950))

    def test_new_feast_gets_its_id(self):
        from database.feasttable import FeastTable
        from feast import Feast
        f = Feast(None)
        self.assertGreater(f.id, 0)
        self.assertEqual(FeastTable().get(f.id)[0], f.id)
        f.data['state'] = 'feast'
        FeastTable().updateData(f)  # used to update cid=-1, i.e. nothing
        self.assertIn('feast', FeastTable().get(f.id)[5])

    def test_cleanup_tokens_statement(self):
        from database.base_table_handler import BaseTableHandler as B
        B.execute("INSERT INTO tokens (token, cid, expires) VALUES ('old', 1, now() - INTERVAL '3 DAYS')", commit=True)
        B.execute("INSERT INTO tokens (token, cid, expires) VALUES ('fresh', 1, now() + INTERVAL '1 DAYS')", commit=True)
        B.execute("DELETE FROM tokens WHERE expires < NOW() - INTERVAL '1 DAYS'", commit=True)
        self.assertEqual(self.scalar("SELECT count(*) FROM tokens WHERE token='old'"), 0)
        self.assertEqual(self.scalar("SELECT count(*) FROM tokens WHERE token='fresh'"), 1)


if __name__ == '__main__':
    unittest.main()
