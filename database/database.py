import datetime
import sqlite3
from config import Config
import postgresql
import os

class Database:
    conn = sqlite3.connect('senechal.db')
    pq  = os.environ['DATABASE_URL']
    if pq.startswith("postgres:"):
        pq = "pq"+pq[8:]
    print(pq)
    db = postgresql.open(pq)

    @staticmethod
    def pgInit():
        db = Database.db
        db.execute("""CREATE TABLE IF NOT EXISTS properties (
            created timestamp without time zone NOT NULL DEFAULT now(), 
            modified timestamp without time zone NOT NULL DEFAULT now(), 
            key text NOT NULL UNIQUE, 
            value text
            )""")
        v = 0
        r = db.query.first("SELECT value FROM properties WHERE key = 'dbversion'")
        print(r)
        if r:
            v = int(r)
        else:
            db.execute("INSERT INTO properties(created, modified, key, value) VALUES(now(), now(),'dbversion',0)")
        if v == 0:
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    created timestamp without time zone NOT NULL DEFAULT now(), 
                    modified timestamp without time zone NOT NULL DEFAULT now(), 
                    year int, 
                    lord bigint,
                    description text,
                    glory int
                    )
                    """)
            db.execute("""CREATE TABLE IF NOT EXISTS lord (
                    created timestamp without time zone NOT NULL DEFAULT now(), 
                    modified timestamp without time zone NOT NULL DEFAULT now(), 
                    year int, 
                    lord bigint,
                    key text,
                    value text
                    )
                    """)
            db.execute("CREATE UNIQUE INDEX idx_lord_key ON lord (lord, key);")
            db.execute("""CREATE TABLE IF NOT EXISTS marks (
                    id SERIAL PRIMARY KEY,
                    created timestamp without time zone NOT NULL DEFAULT now(), 
                    modified timestamp without time zone NOT NULL DEFAULT now(), 
                    year int, 
                    lord bigint,
                    spec text
                    )
                    """)
            db.execute("CREATE UNIQUE INDEX idx_marks_lys ON marks (lord, year, spec);")
            v = 1
            db.execute("UPDATE properties  SET value = 1 WHERE key = 'dbversion'")
        if v == 1:
            c = Database.conn.cursor()
            rows = c.execute("SElECT modified, year, lord, description, glory FROM events ORDER BY id").fetchall()
            print(len(rows))
            insert = db.prepare("INSERT INTO events (created, modified, year, lord, description, glory) VALUES(now(), to_timestamp(substr($1,0,21), 'YYYY-MM-DD hh24:mi:ss')::timestamp, $2, $3, $4, $5)")
            insert.load_rows(rows)
            v = 2
        if v == 2:
            c = Database.conn.cursor()
            rows = c.execute("SElECT last_modified, year, lord, spec FROM marks ORDER BY id").fetchall()
            print(len(rows))
            insert = db.prepare("INSERT INTO marks (created, modified, year, lord, spec) VALUES(now(), to_timestamp(substr($1,0,21), 'YYYY-MM-DD hh24:mi:ss')::timestamp, $2, $3, $4)")
            insert.load_rows(rows)
            v = 3
        db.execute(f"UPDATE properties  SET value = {v} WHERE key = 'dbversion'")

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
                  [str(datetime.datetime.utcnow()), version])
        Database.pgInit()
        Database.conn.commit()
