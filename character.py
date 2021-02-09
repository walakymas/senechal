import json

from database.charactertable import CharacterTable


class Character:
    fallbacks = {
        'SpearExpertise': ['Spear', 'Lance', 'Great Spear'],
        'Law': ['Courtesy', 'Folklore', 'Intrigue'],
        'Music': ['Play (Instrument)']
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

    @staticmethod
    def get_by_memberid(mid):
        record = CharacterTable().get_by_memberid(mid)
        if record:
            return Character(record)

    @staticmethod
    def get_by_id(mid):
        record = CharacterTable().get_by_id(mid)
        if record:
            return Character(record)
        else:
            print(f'get_by_id: {mid} : {record}')

    @staticmethod
    def get_by_name(name):
        record = CharacterTable().get_by_name(name)
        if record:
            return Character(record)

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

