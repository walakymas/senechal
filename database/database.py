import datetime
import sqlite3
from config import Config
from urllib.parse import urlparse
import psycopg2
import os

class Database:
    conn = sqlite3.connect('senechal.db')
    pq = os.getenv('DATABASE_URL')
    print( os.getenv('DATABASE_URL'))
    url = urlparse(pq)
    db = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    @staticmethod
    def initiate():
        print("initiate")
        with Database.db.cursor() as cur:
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
            print(f"PG version: {v}")
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
                for name, ch in Config.charactersOrig.items():
                    mid = None
                    if "memberId" in ch:
                        mid = ch['memberId']
                    url = None
                    if "url" in ch:
                        url = ch['url']

                    insert = cur.execute("""INSERT INTO characters (created, modified, memberid, name, url, data) 
                        VALUES(now(), now(), %s, %s, %s, %s)""",
                                         [mid, ch['name'], url, json.dumps(ch, ensure_ascii=False)])
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
                cur.execute("""ALTER TABLE  tokens ADD tokenstate integer NOT NULL DEFAULT 0""")
                cur.execute("""CREATE TABLE IF NOT EXISTS player (
                        cid bigint PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT  now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        playerstate bigint NOT NULL DEFAULT 0,
                        playerrights bigint NOT NULL DEFAULT 0
                        )
                        """)
                v = 13
            if v == 13:
                cur.execute("""ALTER TABLE  player ADD name varchar NOT NULL DEFAULT 'a' """)
                cur.execute("""ALTER TABLE  player CONSTRAINT UNIQ player_name UNIQUE (name) """)
                cur.execute("""ALTER TABLE  player ADD character bigint """)
                cur.execute("""ALTER TABLE  player ADD memberid bigint """)
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
            if v == 14:
                cur.execute("""CREATE TABLE IF NOT EXISTS p2c (
                        cid bigint PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT  now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        character bigint NOT NULL DEFAULT 0,
                        player bigint NOT NULL DEFAULT 0,
                        connection varchar2(200),
                        comment text
                        )
                        """)
                cur.execute("""CREATE TABLE IF NOT EXISTS p2p (
                        cid bigint PRIMARY KEY,
                        created timestamp without time zone NOT NULL DEFAULT  now(), 
                        modified timestamp without time zone NOT NULL DEFAULT now(),
                        player0 bigint NOT NULL DEFAULT 0,
                        player1 bigint NOT NULL DEFAULT 0,
                        connection varchar2(200),
                        comment text
                        )
                        """)
                v = 15            
            cur.execute(f"UPDATE properties  SET value = {v} WHERE key = 'dbversion'")
            Database.db.commit()

