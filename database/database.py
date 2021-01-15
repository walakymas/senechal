import datetime
import sqlite3
from config import Config


class Database:
    conn = sqlite3.connect('senechal.db')

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
        version = 0;
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
        Database.conn.commit()
