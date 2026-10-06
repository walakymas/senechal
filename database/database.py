import logging
import os
import threading
import time

import psycopg2

log = logging.getLogger(__name__)


class Database:
    # One shared connection is used by the bot (event loop) and by the API
    # (worker threads) in the single-process setup: serialise access to it.
    lock = threading.RLock()

    # The connection is opened on first use (not on import) and reopened when it is
    # closed or found dead after being idle (e.g. the server dropped it).
    _connection = None
    _last_used = 0.0
    IDLE_PING_SECONDS = 60

    @staticmethod
    def connect():
        """Opens a new connection from DATABASE_URL (the whole URL is passed on, so ?sslmode=... is kept)."""
        dsn = os.getenv('DATABASE_URL')
        if not dsn:
            raise RuntimeError("DATABASE_URL is not set")
        return psycopg2.connect(dsn, connect_timeout=10, keepalives=1,
                                keepalives_idle=60, keepalives_interval=10, keepalives_count=5)

    @staticmethod
    def get():
        """The live connection; callers hold Database.lock. Reconnects if needed."""
        conn = Database._connection
        if conn is not None and not conn.closed and time.monotonic() - Database._last_used > Database.IDLE_PING_SECONDS:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                conn.rollback()
            except psycopg2.Error:
                Database.reset()
                conn = None
        if conn is None or conn.closed:
            Database.reset()
            conn = Database._connection = Database.connect()
        Database._last_used = time.monotonic()
        return conn

    @staticmethod
    def reset():
        """Drops the current connection (the next get() opens a new one)."""
        conn, Database._connection = Database._connection, None
        if conn is not None:
            try:
                conn.close()
            except psycopg2.Error:
                pass

    @staticmethod
    def initiate():
        """Creates / migrates the schema; callers hold Database.lock. A failed step rolls everything back."""
        log.info("initiate")
        conn = Database.get()
        try:
            Database._migrate(conn)
        except Exception:
            conn.rollback()
            raise

    @staticmethod
    def _migrate(conn):
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS properties (
                created timestamp without time zone NOT NULL DEFAULT now(), 
                modified timestamp without time zone NOT NULL DEFAULT now(), 
                key text NOT NULL UNIQUE, 
                value text
                )""")
            v = 0
            cur.execute("""SELECT value FROM properties WHERE key = 'dbversion';""")
            r = cur.fetchone()
            if r:
                v = int(r[0])
            else:
                cur.execute("INSERT INTO properties(created, modified, key, value) VALUES(now(), now(),'dbversion',0)")
                cur.execute("INSERT INTO properties(created, modified, key, value) VALUES(now(), now(),'year',481)")
            log.info("PG version: %s", v)
            if v == 0:
                cur.execute("""CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(), 
                        year int, 
                        lord bigint,
                        description text,
                        glory int
                        )
                        """)
                cur.execute("""CREATE TABLE IF NOT EXISTS lord (
                        created timestamp without time zone NOT NULL DEFAULT now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(), 
                        year int, 
                        lord bigint,
                        key text,
                        value text
                        )
                        """)
                cur.execute("CREATE UNIQUE INDEX idx_lord_key ON lord (lord, key);")
                cur.execute("""CREATE TABLE IF NOT EXISTS marks (
                        id SERIAL PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(), 
                        year int, 
                        lord bigint,
                        spec text
                        )
                        """)
                cur.execute("CREATE UNIQUE INDEX idx_marks_lys ON marks (lord, year, spec);")
                v = 1
                cur.execute("UPDATE properties SET value = 1 WHERE key = 'dbversion'")
                cur.execute("UPDATE properties SET value = 1 WHERE key = 'dbversion'")
                v = 3
            if v == 3:
                cur.execute("DROP INDEX IF EXISTS idx_lord_key;")
                cur.execute("CREATE UNIQUE INDEX idx_lord_year_key ON lord (lord, year, key);")
                v = 4
            if v == 4:
                cur.execute("""CREATE TABLE IF NOT EXISTS characters (
                        id SERIAL PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(), 
                        memberid bigint, 
                        name varchar not null, 
                        url varchar, 
                        data text
                        )
                        """)
                v = 7
            if v == 7:
                cur.execute("TRUNCATE characters")
                import json
                v = 8
            if v == 8:
                cur.execute("ALTER TABLE characters ADD role varchar")
                v = 9
            if v == 9:
                cur.execute("""CREATE TABLE IF NOT EXISTS tokens (
                        id SERIAL PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        expires timestamp without time zone NOT NULL, 
                        cid bigint, 
                        token varchar not null
                        )
                        """)
                v = 10
            if v == 10:
                cur.execute("""ALTER TABLE  marks ADD dbid integer""")
                cur.execute("""UPDATE marks SET dbid = (SELECT id FROM characters WHERE characters.memberid = marks.lord);""")
                cur.execute("CREATE UNIQUE INDEX idx_marks_iys ON marks (dbid, year, spec);")
                v = 11
            if v == 11:
                cur.execute("""ALTER TABLE  events ADD dbid integer""")
                cur.execute("""UPDATE events SET dbid = (SELECT id FROM characters WHERE characters.memberid = events.lord);""")
                v = 12
            if v == 12:
                cur.execute("""ALTER TABLE tokens ADD tokenstate integer NOT NULL DEFAULT 0""")
                cur.execute("""ALTER TABLE tokens ADD CONSTRAINT un_token UNIQUE (token)""")
                cur.execute("""CREATE TABLE IF NOT EXISTS player (
                        cid bigint PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT  now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        playerstate bigint NOT NULL DEFAULT 0,
                        playerrights bigint NOT NULL DEFAULT 0,
                        did bigint NOT NULL unique
                        )
                        """)
                v = 13
            if v == 13:
                # `name` is used by the token queries and by the v14 insert below (the old ALTERs were commented out,
                # which broke fresh installs); IF NOT EXISTS keeps already migrated databases untouched
                cur.execute("""ALTER TABLE  player ADD COLUMN IF NOT EXISTS name varchar """)
                cur.execute("""ALTER TABLE  player ADD character bigint """)
                cur.execute("""ALTER TABLE  characters ADD player bigint """)
                cur.execute("""CREATE TABLE IF NOT EXISTS checks (
                        cid bigint PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT  now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        character bigint NOT NULL DEFAULT 0,
                        command text,
                        result text
                        )
                        """)
                v = 14
            if v == 14:
                cur.execute("""CREATE TABLE IF NOT EXISTS p2c (
                        cid bigint PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT  now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        character bigint NOT NULL DEFAULT 0,
                        player bigint NOT NULL DEFAULT 0,
                        connection varchar,
                        comment text
                        )
                        """)
                cur.execute("""CREATE TABLE IF NOT EXISTS c2c (
                        cid bigint PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT  now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        c0 bigint NOT NULL DEFAULT 0,
                        c1 bigint NOT NULL DEFAULT 0,
                        connection varchar,
                        comment text
                        )
                        """)
                cur.execute("""create sequence player_id_seq""")
                cur.execute("""ALTER TABLE player ALTER COLUMN cid SET DEFAULT nextval('player_id_seq'::regclass)""")
                cur.execute("""ALTER TABLE player ADD COLUMN IF NOT EXISTS did bigint """)
                cur.execute("""INSERT INTO player (character,did, name) SELECT id, memberid, name from characters WHERE memberid IS NOT NULL """)
                cur.execute("""UPDATE player set playerrights = 1023 WHERE did IN (470683159889969153, 778706677120892958)""")
                cur.execute("""create sequence main_seq;""")
                cur.execute("""ALTER TABLE p2c ALTER COLUMN cid SET DEFAULT nextval('main_seq'::regclass)""")
                cur.execute("""ALTER TABLE c2c ALTER COLUMN cid SET DEFAULT nextval('main_seq'::regclass)""")
                cur.execute("""ALTER TABLE checks ALTER COLUMN cid SET DEFAULT nextval('main_seq'::regclass)""")
                v = 15                            
            if v == 15:
                cur.execute("""CREATE TABLE IF NOT EXISTS feast (
                        cid bigint PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT  now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        title varchar,
                        description text,
                        data text,
                        deck text
                        )
                        """)
                cur.execute("""ALTER TABLE feast ALTER COLUMN cid SET DEFAULT nextval('main_seq'::regclass)""")
                v = 16

            # New migration step: create maps table
            if v == 16:
                cur.execute("""CREATE TABLE IF NOT EXISTS maps (
                        id SERIAL PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT now(),
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        url varchar,
                        category varchar,
                        ord integer,
                        name varchar
                        )""")
                cur.execute("ALTER TABLE maps ALTER COLUMN id SET DEFAULT nextval('main_seq'::regclass)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_maps_ord ON maps (ord);")
                v = 17

            # c2c / p2c are written with ON CONFLICT (c0, c1) / (player, character), which needs these unique indexes.
            # Duplicates (if any) are collapsed first: the newest row (highest cid) of a pair is kept.
            if v == 17:
                cur.execute("DELETE FROM c2c a USING c2c b WHERE a.c0 = b.c0 AND a.c1 = b.c1 AND a.cid < b.cid")
                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_c2c_c0_c1 ON c2c (c0, c1)")
                cur.execute("DELETE FROM p2c a USING p2c b WHERE a.player = b.player AND a.character = b.character AND a.cid < b.cid")
                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_p2c_player_character ON p2c (player, character)")
                v = 18

            cur.execute("UPDATE properties  SET value = %s, modified=now() WHERE key = 'dbversion'", (v,))
            conn.commit()                      

