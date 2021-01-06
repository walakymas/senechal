import datetime
import sqlite3


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
        c.execute("REPLACE INTO properties (last_modified, key, value) VALUES(?,'dbversion',?);",
                  [str(datetime.datetime.utcnow()), version])
        Database.conn.commit()

    @staticmethod
    def listProperties():
        cur = Database.conn.cursor()
        cur.execute("SELECT * FROM properties ORDER BY key")
        return cur.fetchall()

    @staticmethod
    def setProperties(key, value):
        cur = Database.conn.cursor()
        cur.execute("REPLACE INTO properties (last_modified, key, value) VALUES(?,?,?);",
                    [str(datetime.datetime.utcnow()), key, value])
        Database.conn.commit()

    @staticmethod
    def getProperties(key):
        cur = Database.conn.cursor()
        cur.execute("SELECT * FROM properties WHERE key = ?;", [key])
        return cur.fetchone()

    @staticmethod
    def listLord():
        cur = Database.conn.cursor()
        cur.execute("SELECT * FROM lord ORDER BY lord, key")
        return cur.fetchall()

    @staticmethod
    def setLord(lord, year, key, value):
        cur = Database.conn.cursor()
        cur.execute("REPLACE INTO lord (last_modified, lord, year, key, value) VALUES(?,?,?,?);",
                    [str(datetime.datetime.utcnow()), lord, year, key, value])
        Database.conn.commit()

    @staticmethod
    def getLord(lord, year, key):
        cur = Database.conn.cursor()
        cur.execute("SELECT * FROM lord WHERE lord=?, year=?, key = ?;", [lord, year, key])
        return cur.fetchone()

    @staticmethod
    def getLordByValue(year, key, value):
        cur = Database.conn.cursor()
        cur.execute("SELECT * FROM lord WHERE year=?, key = ?, value=?;", [year, key, value])
        return cur.fetchone()

    @staticmethod
    def listMark():
        cur = Database.conn.cursor()
        cur.execute("SELECT * FROM marks ORDER BY lord, year, spec")
        return cur.fetchall()

    @staticmethod
    def setMark(lord, year, spec):
        cur = Database.conn.cursor()
        cur.execute("REPLACE INTO marks (last_modified, lord, year, spec) VALUES(?,?,?,?);",
                    [str(datetime.datetime.utcnow()), lord, year, spec])
        Database.conn.commit()

    @staticmethod
    def getMarks(lord, year):
        cur = Database.conn.cursor()
        cur.execute("SELECT * FROM marks WHERE lord=?, year=?;", [lord, year])
        return cur.fetchone()

    @staticmethod
    def delMark(id):
        cur = Database.conn.cursor()
        cur.execute("DELETE FROM marks WHERE id=?;", [id])
        Database.conn.commit()
