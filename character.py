from datetime import datetime
import json

from database.charactertable import CharacterTable


class Character:
    fallbacks = {
        'SpearExpertise': ['Spear', 'Lance', 'Great Spear'],
        'Law': ['Courtesy', 'Folklore', 'Intrigue'],
        'Music': ['Play (Instrument)', 'Signing', 'Compose'],
        'Distaff': ['Stewardship', 'Industry']
    }

    def __init__(self, record):
        self.id = record[0]
        self.created = record[1]
        self.modified = record[2]
        self.memberid = record[3]
        self.name = record[4]
        self.url = record[5]
        self.json = record[6]
        self.data = json.loads(self.json)

    def get_memberid(self):
        return self.memberid

    def get_data(self, fallback=True):
        if fallback and 'skills' in self.data:
            for n, sg in self.data['skills'].items():
                up = {}
                for sn, sv in sg.items():
                    if sn in Character.fallbacks:
                        for f in Character.fallbacks[sn]:
                            if f not in sg or str(sg[f])[:1] == '.' or sv > sg[f]:
                                up[f] = sv
                sg.update(up)
        return self.data

    cache = {}
    cache_timeline = 0
    @staticmethod
    def check_cache():
        now = datetime.timestamp(datetime.now())
        print("timestamp =", now)
        if now > Character.cache_timeline:
            Character.cache = {}
            Character.cache_timeline = 60+now ## Egy perc cache

    @staticmethod
    def get_by_memberid(mid, force=False):
        if not force:
            Character.check_cache()
        if force or mid in Character.cache:
            return Character.cache[mid]
        else:
            record = CharacterTable().get_by_memberid(mid)
            if record:
                c = Character(record)
                Character.cache[mid] = c
                return c

    @staticmethod
    def get_by_id(mid, force=False):
        if not force:
            Character.check_cache()
        if force or mid in Character.cache:
            return Character.cache[mid]
        else:
            record = CharacterTable().get_by_id(mid)
            if record:
                c = Character(record)
                Character.cache[mid] = c
                return c

    @staticmethod
    def get_by_name(name, force=False):
        if not force:
            Character.check_cache()
        if force or name in Character.cache:
            return Character.cache[name]
        else:
            record = CharacterTable().get_by_name(name)
            if record:
                c = Character(record)
                Character.cache[name] = c
                return c

    @staticmethod
    def list_by_name(name=None):
        for row in CharacterTable().list():
            if (not name) or (name == '*') or (name.lower() in row[4].lower()):
                yield Character(row)

    @staticmethod
    def pcs(name=None):
        for c in Character.list_by_name(name):
            if c.memberid:
                yield c

    @staticmethod
    def npcs(name=None):
        for c in Character.list_by_name(name):
            if not c.memberid:
                yield c

