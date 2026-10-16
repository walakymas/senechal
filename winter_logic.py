"""The winter phase and the mark update, shared by the bot (`!winter`, `!mark update`) and the web API.

A mark (marks table) records that a skill / trait / passion was used successfully in a year. The winter rolls a d20
for every Unchecked mark: at most the value -> Failed, above it (or a 20 against a value over 20) -> Increase.
The update raises the value of the Increase marks by one and makes them Updated.
"""
import json
import logging

from character import Character
from config import Config
from database.c2ctable import C2CTable
from database.charactertable import CharacterTable
from database.eventstable import EventsTable
from database.markstable import MarksTable

log = logging.getLogger(__name__)

# marks table columns (see MarksTable)
ID, MODIFIED, SPEC, STATUS = 0, 2, 5, 7
MARKS_PER_FIELD = 10


def mark_status(roll, value):
    """The status of a mark after a d20 roll against the value of the skill / trait / passion."""
    if roll > value or (value > 20 and roll == 20):
        return MarksTable.INCREASE
    return MarksTable.FAILED


def resolve_mark(data, spec):
    """(type, name, value, ...) of the skill / trait / passion a mark names (the exact name wins over a prefix match),
    or None when the character has no such thing (any more). Stats cannot be marked."""
    from utils import get_checkable
    Config.senechal()
    try:
        found = [f for f in get_checkable(data, spec) if f[0] != 'stat']
    except (KeyError, TypeError, ValueError):
        return None
    exact = [f for f in found if f[1].lower() == spec.lower()]
    found = exact or found
    return found[0] if found else None


class WinterResult:
    """The fields of the winter report: (name, value, code) where `code` values are shown as a code block."""

    def __init__(self, char, year):
        self.char = char
        self.year = year
        self.fields = []

    def add(self, name, value, code=True):
        self.fields.append((name, value, code))

    def embed_fields(self):
        """(name, value, inline) tuples for utils.send_embed_fields."""
        return [(name, f"```{value}```" if code else value, False) for name, value, code in self.fields]

    def text(self):
        """The whole report as plain text (it is stored as an event of the character)."""
        lines = [f"Winter {self.year}"]
        for name, value, code in self.fields:
            lines.append(f"{name}\n{str(value).strip()}")
        return "\n\n".join(lines)


def check_marks(char, year, force=False, with_date=False):
    """Rolls the Unchecked marks of the character in the year (all but the Updated ones with `force`) and stores the
    result in the marks table; the already checked ones are reported from their status. Returns the report lines."""
    from utils import dice
    data = char.get_data()
    lines = []
    for row in MarksTable().list(dbid=int(char.id), year=year):
        found = resolve_mark(data, row[SPEC])
        if found is None:
            continue
        name, value = found[1], found[2]
        status = row[STATUS]
        roll = '--'
        if status == MarksTable.UNCHECKED or (force and status != MarksTable.UPDATED):
            roll = dice(20)
            status = mark_status(roll, value)
            MarksTable().set_status(row[ID], status)
        effect = {MarksTable.UNCHECKED: '?', MarksTable.FAILED: '---'}.get(status, status)
        date = f"{str(row[MODIFIED])[:10]} " if with_date else ""
        lines.append(f"{date}{name:15} {roll:>2} vs {value:2}  {effect}")
    return lines


def run_winter(char, force=False, record_event=True):
    """The winter of a character: economy, horses, marks (own and of the connected characters), extra glory.
    The report is also stored as a new event of the character in the current year. Returns a WinterResult."""
    from utils import dice, check, winterData
    winter = winterData(char)
    year = MarksTable().year()
    result = WinterResult(char, year)
    major = dice(6)
    msg = f"Gazdaság: {('Terrible', 'Bad', 'Normal', 'Normal', 'Good', 'Excellent')[major - 1]} ({major})\n"
    (c, t, dobas, siker) = check(int(winter['stewardship']), 0, False)
    if major in (1, 2):
        msg += f"Stewardship({winter['stewardship']}): {dobas} {t}  {('Kemény munkával kivédtétek a bajt', 'Szegény lovag vagy')[siker >= 3]} \n"
    elif major == 5:
        msg += f"Extra bevétel: {dice(20)} \n"
    elif major == 6:
        msg += f"Stewardship({winter['stewardship']}): {dobas} {t}  {('Gazdag lovag vagy', 'Nem sikerült kihasználni a remek időt')[siker >= 3]} \n"
    result.add(f"{year} tele", msg)
    msg = ""
    for h in winter['horses']:
        msg += f"  {h}: {('Egészséges', 'Megdöglött vagy tönkrement')[dice(20) < 3]}\n"
    result.add("Lovak", msg)

    charId = int(char.id)
    lines = check_marks(char, year, force)
    for i in range(0, len(lines), MARKS_PER_FIELD):
        header = "Spec              Dobás   Hatás\n" if i == 0 else ""
        result.add("Pipák", header + "\n".join(lines[i:i + MARKS_PER_FIELD]) + "\n")

    xp = 0
    for n, v in char.data['traits'].items():
        if v >= 16:
            xp += v
        elif v <= 4:
            xp += 20 - v
    for n, v in char.data['passions'].items():
        if int(v) >= 16:
            xp += int(v)
    if xp > 0:
        result.add("Extra Glory", f"`{xp}`", code=False)

    # connected characters: the 'npcs' block of the character plus the c2c connections (either direction)
    npcs = dict(char.data.get('npcs', {}))
    known = {int(f['dbid']) for f in npcs.values() if 'dbid' in f}
    for row in C2CTable().list(charId):
        other = int(row[4]) if int(row[3]) == charId else int(row[3])
        if other != charId and other not in known:
            known.add(other)
            connection = row[5] or ''
            npcs[f"c2c:{other}"] = {'dbid': other, 'connection': connection, 'role': connection.lower()}
    for nf, f in npcs.items():
        s = ""
        if 'dbid' in f:
            npc = Character.get_by_id(f['dbid'])
            if npc is None:
                continue
            if 'Deceased' in npc.data.get('main', {}):
                s = f"NPC is dead ({npc.data['main']['Deceased']})\n"
            else:
                if 'role' in f and (f['role'] == 'wife' or f['role'] == 'lover'):
                    birth = 0
                    con = npc.data['stats']['con']
                    if 'Birth' in npc.data['main']:
                        birth = npc.data['main']['Birth']
                    elif 'birth' in npc.data['main']:
                        birth = npc.data['main']['birth']
                    s += f"Con: {con}, Birth: {birth} \n"
                s += "Modified   Spec              Dobás   Hatás\n"
                s += "".join(line + "\n" for line in check_marks(npc, year, force, with_date=True))
            if s != "":
                result.add(f"{npc.data['name']} ({f['connection']})", s)
        else:
            if 'skills' in f:
                for n, v in f['skills'].items():
                    if v < 15 or (v <= 20 and dice(6) == 6) or (v > 20 and dice(20) == 20):
                        s += f"{n} `{v}` -> `{v + 1}`\n"
            if s != "":
                result.add(f"{nf} ({f['connection']})", s, code=False)
    if record_event:
        EventsTable().insert(charId, result.text(), 0, year)
    return result


def _bump(data, found):
    """Raises the thing `found` (see resolve_mark) by one in the raw character data; returns (old, new)."""
    kind, name, old = found[0], found[1], found[2]
    if kind == 'skill':
        for group in data['skills'].values():
            if name in group:
                group[name] = new = old + 1
                return old, new
    elif kind == 'pass':
        data['passions'][name] = new = old + 1
        return old, new
    elif kind == 'trait':
        for positive, negative in Config.senechalConfig['traits']:
            if name in (positive, negative):
                key = positive.lower()[:3]
                stored = int(data['traits'][key])
                # a trait and its opposite add up to 20: raising the opposite lowers the stored value
                stored = min(20, stored + 1) if name == positive else max(0, stored - 1)
                data['traits'][key] = stored
                return old, (stored if name == positive else 20 - stored)
    raise KeyError(name)


def update_marks(dbid, year):
    """Raises the value of the Increase marks of the character in the year by one and makes them Updated.
    The raw character data is changed (not the fallback-extended one of Character.get_data). Returns
    [(name, old, new), ...]."""
    rows = [r for r in MarksTable().list(dbid=int(dbid), year=int(year)) if r[STATUS] == MarksTable.INCREASE]
    if not rows:
        return []
    record = CharacterTable().get_by_id(int(dbid))
    if record is None:
        raise ValueError(f"No such character: {dbid}")
    data = json.loads(record[6])
    changes, done = [], []
    for row in rows:
        found = resolve_mark(data, row[SPEC])
        if found is None:
            continue
        try:
            old, new = _bump(data, found)
        except KeyError:
            continue
        changes.append((found[1], old, new))
        done.append(row[ID])
    if done:
        CharacterTable().set_json(int(dbid), json.dumps(data, ensure_ascii=False))
        MarksTable().set_status_many(done, MarksTable.UPDATED)
        Character.get_by_id(int(dbid), True)
    return changes
