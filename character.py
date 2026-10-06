import json
import logging
import threading
import time

from config import Config
from database.charactertable import CharacterTable
from database.playertable import PlayerTable

log = logging.getLogger(__name__)


class Character:
    def __init__(self, record):
        self.id = record[0]
        self.created = record[1]
        self.modified = record[2]
        # Discord id of the player of the character (the memberid column was replaced by the player table)
        if len(record) > 9:  # CharacterTable records carry the player's did (index 9)
            self.memberid = int(record[9]) if record[9] else None
        else:
            self.memberid = PlayerTable().did_by_character(self.id)
        self.name = record[4]
        self.url = record[5]
        self.json = record[6]
        self.data = json.loads(self.json)
        self.data['memberId'] = f'{self.memberid}' if self.memberid else None
        log.debug("memberId: %s", self.data['memberId'])
        if len(record) > 8 and record[8]:
            self.data['player'] = record[8]
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
                "horses": [  # no stewardship here: winterData falls back to the character's own skill
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
            spec = 'Sword'
            try:
                if self.data['combat']['weapon'] != 'empty':
                   spec = self.data['combat']['weapon']
            except (KeyError, TypeError):
                pass
            
        weapon = Config.weapon(spec)
        weapon['damage'] += self.get_damage()
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

    # Cache of loaded characters: a positive entry lives CACHE_TTL seconds, "not found" only NEGATIVE_TTL seconds
    # (so that a player who has just got a character is not "unknown" for long). The API and the bot share it.
    CACHE_TTL = 60
    NEGATIVE_TTL = 10
    cache = {}
    cache_lock = threading.RLock()
    MISSING = object()

    @staticmethod
    def _cache_get(key):
        with Character.cache_lock:
            entry = Character.cache.get(key)
            if entry is None:
                return Character.MISSING
            value, expires = entry
            if time.monotonic() > expires:
                del Character.cache[key]
                return Character.MISSING
            return value

    @staticmethod
    def _cache_put(key, value):
        with Character.cache_lock:
            ttl = Character.CACHE_TTL if value is not None else Character.NEGATIVE_TTL
            Character.cache[key] = (value, time.monotonic() + ttl)

    @staticmethod
    def get_by_memberid(mid, force=False):
        mid = int(mid)
        key = ('member', mid)
        if not force:
            cached = Character._cache_get(key)
            if cached is not Character.MISSING:
                return cached
        log.debug("get_by_memberid %s from the database", mid)
        record = CharacterTable().get_by_memberid(mid)
        c = Character(record) if record else None
        Character._cache_put(key, c)
        return c

    @staticmethod
    def get_by_id(mid, force=False):
        mid = int(mid)
        key = ('id', mid)
        if not force:
            cached = Character._cache_get(key)
            if cached is not Character.MISSING:
                return cached
        record = CharacterTable().get_by_id(mid)
        c = Character(record) if record else None
        Character._cache_put(key, c)
        return c

    @staticmethod
    def get_many_by_id(ids):
        """{id: Character} for the existing ones among `ids`: the cached ones are reused, the rest is loaded
        with a single query."""
        found = {}
        missing = []
        for mid in {int(i) for i in ids}:
            cached = Character._cache_get(('id', mid))
            if cached is Character.MISSING:
                missing.append(mid)
            elif cached is not None:
                found[mid] = cached
        if missing:
            records = CharacterTable().get_by_ids(missing)
            for mid in missing:
                record = records.get(mid)
                c = Character(record) if record else None
                Character._cache_put(('id', mid), c)
                if c:
                    found[mid] = c
        return found

    @staticmethod
    def get_by_name(name, force=False):
        key = ('name', name.lower())
        if not force:
            cached = Character._cache_get(key)
            if cached is not Character.MISSING:
                return cached
        record = CharacterTable().get_by_name(name)
        c = Character(record) if record else None
        Character._cache_put(key, c)
        return c

    @staticmethod
    def list_by_name(name=None):
        for row in CharacterTable().list():
            if (not name) or (name == '*') or (name.lower() in row[4].lower()):
                yield Character(row)

    @staticmethod
    def pcs(name=None, extra=None):
        """The player characters; with a name only those whose name contains it (None / '*': all)."""
        for c in CharacterTable().get_pcs():
            if (not name) or (name == '*') or (name.lower() in c[4].lower()):
                yield Character(c)

    @staticmethod
    def npcs(name=None):
        for c in Character.list_by_name(name):
            if not c.memberid:
                yield c
