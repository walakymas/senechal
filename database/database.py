import datetime
import sqlite3
from config import Config
from urllib.parse import urlparse
import psycopg2
import os

class Database:
    conn = sqlite3.connect('senechal.db')
    pq  = os.environ['DATABASE_URL']
    url = urlparse(pq)
    db = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    @staticmethod
    def pgInit():
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
                cur.execute("UPDATE properties  SET value = 1 WHERE key = 'dbversion'")
            if v == 1:
                c = Database.conn.cursor()
                rows = c.execute("SElECT modified, year, lord, description, glory FROM events ORDER BY id").fetchall()
                print(len(rows))
                for row in rows:
                    cur.execute("INSERT INTO events (created, modified, year, lord, description, glory) VALUES(now(), to_timestamp(substr(%s,0,21), 'YYYY-MM-DD hh24:mi:ss')::timestamp, %s, %s, %s, %s)", row)
                v = 2
            if v == 2:
                c = Database.conn.cursor()
                rows = c.execute("SElECT last_modified, year, lord, spec FROM marks ORDER BY id").fetchall()
                print(len(rows))
                for row in rows:
                    insert = cur.execute("INSERT INTO marks (created, modified, year, lord, spec) VALUES(now(), to_timestamp(substr(%s,0,21), 'YYYY-MM-DD hh24:mi:ss')::timestamp, %s, %s, %s)", row)
                v = 3
            cur.execute(f"UPDATE properties  SET value = {v} WHERE key = 'dbversion'")
            Database.db.commit()

    @staticmethod
    def initiate():
        print("initiate")
        c = Database.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS properties (
            last_modified text, 
            key text, 
            value text
            )
            """)
        c.execute("SELECT value FROM properties WHERE key='dbversion'")
        rows = c.fetchall()
        version = 0
        if len(rows) == 1:
            version = int(rows[0][0])
            print(f"Version: {version}")
        else:
            c.execute("INSERT INTO properties(last_modified, key, value) VALUES(?,'dbversion',0)",
                      [str(datetime.datetime.utcnow())])
        if version == 0:
            print("Update 1")
            c.execute("""CREATE TABLE IF NOT EXISTS events (
                id int,
                last_modified text, 
                year int, 
                lord int,
                description text,
                glory int
                )
                """)
            version = 1
        if version == 1:
            print("Update 2")
            c.execute("CREATE UNIQUE INDEX idx_properties_key ON properties (key);")
            version = 2
        if version == 2:
            print("Update 3")
            c.execute("""CREATE TABLE IF NOT EXISTS marks (
                last_modified text, 
                year int, 
                lord int,
                spec text,
                id INTEGER PRIMARY KEY
                )
                """)
            c.execute("CREATE UNIQUE INDEX idx_marks_lys ON marks (lord, year, spec);")
            version = 3
        if version == 3:
            print("Update 4")
            c.execute("""CREATE TABLE IF NOT EXISTS lord (
                last_modified text, 
                year int, 
                lord int,
                key text,
                value text
                )
                """)
            c.execute("CREATE UNIQUE INDEX idx_lord_key ON lord (lord, key);")
            version = 4
        if version == 4:
            print("Update 5")
            c.execute("DROP TABLE events")
            c.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                modified text, 
                created text, 
                year int, 
                lord int,
                description text,
                glory int
                )
                """)
            version = 5
        if version == 5:
            from database.eventstable import EventsTable
            print("Update 6")
            et = EventsTable()
            for pc in Config.pcs():
                for e in pc['events']:
                    et.insert(pc['memberId'], e['description'], e['glory'], e['year'])
            version = 6
        c.execute("REPLACE INTO properties (last_modified, key, value) VALUES(?,'dbversion',?);",
                  [str(datetime.datetime.now()), version])
        Database.pgInit()
        Database.conn.commit()
