from datetime import datetime
import json

from config import Config
from database.charactertable import CharacterTable


class Character:
    def __init__(self, record):
        self.id = record[0]
        self.created = record[1]
        self.modified = record[2]
        self.memberid = record[3]
        self.name = record[4]
        self.url = record[5]
        self.json = record[6]
        self.data = json.loads(self.json)
        self.data['dbid'] = self.id
        if not 'stats' in self.data:
            self.data['stats'] = {"siz": 10, "dex": 10, "str": 10, "con": 10, "app": 10}
        if not 'traits' in self.data:
            self.data['traits'] = { "cha": 10, "ene": 10, "for": 10, "gen": 10, "hon": 10, "jus": 10, "mer": 10, "mod": 10, "pru": 10, "spi": 10, "tem": 10, "tru": 10, "val": 10 }
        if not 'passions' in self.data:
            self.data['passions'] = { }
        if not 'skills' in self.data:
            self.data['skills'] = {}
        if not 'Other' in self.data['skills']:
            self.data['skills']['Other'] = {}
        if not 'Combat' in self.data['skills']:
            self.data['skills']['Combat'] = {}
        if not 'Weapons' in self.data['skills']:
            self.data['skills']['Weapons'] = {}
        if not 'main' in self.data:
            self.data['main'] = { }
        if not 'description' in self.data:
            self.data['description'] =  "???"
        if not 'army' in self.data:
            self.data['army'] =  {
                "Old Knights": 0,
                "Middle-aged Knights": 0,
                "Young Knights": 0,
                "Other Lineage Men": 0,
                "Levy": 0
            }
        if not 'winter' in self.data:
            self.data['winter'] = {
                "stewardship_": 13,
                "horses": [
                    "charger",
                    "rouncy",
                    "rouncy",
                    "sumpter",
                    "sumpter"
                ]
            }
        if not 'combat' in self.data:
            self.data['combat'] = {
                "weapon": "None",
                "shield": "None",
                "armor": "Clothing",
                "spec": []
            }
        if not 'health' in self.data:
            self.data['health'] = {"chirurgery": 0, "changes": []}
        self.weapon = self.get_weapon(self.data['combat']['weapon'])
        if not '2hd' in self.weapon['extra']:
            self.shield = Config.shield(self.data['combat']['shield'])
        else:
            self.shield = Config.shield('None')
        self.armor = Config.armor(self.data['combat']['armor'])
        self.effective_dexterity = self.data['stats']['str'] + self.armor['red'] + self.shield['red']
        self.religion = None

    def get_damage(self):
        return round((self.data['stats']['str'] + self.data['stats']['siz']) / 6)

    def get_weapon(self, spec=None):
        if not spec:
            if self.data['combat']['weapon'] == 'empty':
                spec = 'Sword'
            else:
                spec = self.data['combat']['weapon']
        weapon = Config.weapon(spec)
        weapon['damage'] += round((int(self.data['stats']['str']) + int(self.data['stats']['siz'])) / 6)
        return weapon

    def get_armor(self, spec):
        armor = Config.armor(spec)
        return armor

    def get_memberid(self):
        return self.memberid

    def get_data(self, fallback=True):
        if fallback and 'skills' in self.data:
            for n, sg in self.data['skills'].items():
                up = {}
                for sn, sv in sg.items():
                    if sn in Config.senechal()['fallbacks']:
                        for f in Config.senechal()['fallbacks'][sn]:
                            if f not in sg or str(sg[f])[:1] == '.' or sv > sg[f]:
                                up[f] = sv
                sg.update(up)

        return self.data

    cache = {}
    cache_timeline = 0
    @staticmethod
    def check_cache():
        now = datetime.timestamp(datetime.now())
        if now > Character.cache_timeline:
            Character.cache = {}
            Character.cache_timeline = 60+now ## Egy perc cache

    @staticmethod
    def get_by_memberid(mid, force=False):
        print(f"get_by_memberid {mid} {force}")
        if not force:
            Character.check_cache()
        if not force and mid in Character.cache:
            return Character.cache[mid]
        else:
            print(f"get_by_memberid db")
            record = CharacterTable().get_by_memberid(mid)
            if record:
                print(f"get_by_memberid db")
                c = Character(record)
                Character.cache[mid] = c
                return c

    @staticmethod
    def get_by_id(mid, force=False):
        if not force:
            Character.check_cache()
        if not force and mid in Character.cache:
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
        if not force and name in Character.cache:
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
    def pcs(name=None, extra=None):
        for c in Character.list_by_name(name):
            if c.memberid and (extra or not (
                    'role' in c.data
                    and (
                           c.data['role'] == 'Lord'
                        or c.data['role'] == 'King'
                        or c.data['role'] == 'Retired'
                    )
            )):
                yield c

    @staticmethod
    def npcs(name=None):
        for c in Character.list_by_name(name):
            if not c.memberid:
                yield c

