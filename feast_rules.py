"""Pure rules of the Book of Feasts (no database, no config access) - see documentation/feast-rules.md."""

SEATS = ('above', 'near', 'below', 'floor')
ACTIVITIES = ('card', 'gossip', 'indulge', 'flirt', 'game', 'pass')
RESULTS = ('critical', 'success', 'failure', 'fumble')

MIN_CARD_GLORY = 1000          # Table 1.3: Knight/Lady (1,000+ Glory) draws 1 card, below that none
GLORY_PER_EXTRA_CARD = (1000, 2000, 4000, 8000, 16000, 32000)   # 1 .. 6 cards
MAX_GENIALITY_MODIFIER = 10
MAX_APP_BONUS = 10

# trait key -> (positive name, opposite name); a trait of 16+ makes the positive one "significant", 4- the opposite one
TRAIT_PAIRS = {
    'cha': ('chaste', 'lustful'), 'ene': ('energetic', 'lazy'), 'for': ('forgiving', 'vengeful'),
    'gen': ('generous', 'selfish'), 'hon': ('honest', 'deceitful'), 'jus': ('just', 'arbitrary'),
    'mer': ('merciful', 'cruel'), 'mod': ('modest', 'proud'), 'pru': ('prudent', 'reckless'),
    'spi': ('spiritual', 'worldly'), 'tem': ('temperate', 'indulgent'), 'tru': ('trusting', 'suspicious'),
    'val': ('valorous', 'cowardly'),
}
SIGNIFICANT = 16


def significant_traits(traits, passions=None):
    """Names (lowercase) of the traits (either side of a pair) and passions that are 16 or more."""
    result = []
    for key, value in (traits or {}).items():
        pair = TRAIT_PAIRS.get(key)
        if pair is None or not isinstance(value, (int, float)):
            continue
        if value >= SIGNIFICANT:
            result.append(pair[0])
        if 20 - value >= SIGNIFICANT:
            result.append(pair[1])
    for name, value in (passions or {}).items():
        if isinstance(value, (int, float)) and value >= SIGNIFICANT:
            result.append(str(name).lower())
    return result


def app_bonus(jewelry=0, fashion=0):
    """Modifier of the APP roll: +1 per GBP 1 of jewelry and the Fashion skill, at most +10."""
    return max(0, min(MAX_APP_BONUS, jewelry + fashion))


def clamp_geniality_modifier(geniality):
    """Geniality modifies APP and the courtly skills by at most +/-10."""
    return max(-MAX_GENIALITY_MODIFIER, min(MAX_GENIALITY_MODIFIER, geniality))


def seat_from_app_result(result):
    """Table 1.1 for a non-fumble result."""
    return {'critical': 'above', 'success': 'near', 'failure': 'below'}[result]


def seat_after_fumble(second_result):
    """A fumbled APP roll is rolled again (a fumble counts as a failure now) and the seat is one position lower."""
    if second_result == 'fumble':
        second_result = 'failure'
    return SEATS[min(SEATS.index(seat_from_app_result(second_result)) + 1, len(SEATS) - 1)]


def seat_geniality(position, fumbled=False):
    """Geniality per round for the seating area."""
    if position == 'above':
        return 2
    if position == 'near':
        return 1
    if position == 'floor':
        return -2 if fumbled else -1
    return 0


def number_of_cards(glory, position=None):
    """Cards drawn per round: none Above the Salt or below 1,000 Glory, then one more at each doubling."""
    if position == 'above' or glory is None or glory < MIN_CARD_GLORY:
        return 0
    return sum(1 for limit in GLORY_PER_EXTRA_CARD if glory >= limit)


def activity_geniality(result):
    """Gossip / Indulge / Flirt / Game: success +1, critical +2, fumble -1."""
    return {'critical': 2, 'success': 1, 'fumble': -1}.get(result, 0)


def first_round_requirement(significant):
    """Round 1: Indulgent 16+ needs a Temperate roll for anything but Indulge, Lustful 16+ a Chaste roll for anything but Flirt.
    Returns {activity that needs no roll: roll needed otherwise}."""
    required = {}
    if 'indulgent' in significant:
        required['indulge'] = 'temperate'
    if 'lustful' in significant:
        required['flirt'] = 'chaste'
    return required


def leave_geniality(geniality):
    """Leaving the feast (for any reason) drops all positive Geniality; a negative score is kept."""
    return min(geniality, 0)


def final_glory(guests, royal=False):
    """Glory at the end of the feast. `guests` maps id -> {'geniality': int, 'position': seat}.
    The highest Geniality gets geniality * 10 (ties share it), everybody else their positive Geniality;
    +100 for a royal feast and a further +100 for sitting Above the Salt."""
    if not guests:
        return {}
    best = max(g.get('geniality', 0) for g in guests.values())
    result = {}
    for cid, g in guests.items():
        geniality = g.get('geniality', 0)
        glory = geniality * 10 if geniality == best else max(geniality, 0)
        glory = max(glory, 0)
        if royal:
            glory += 100
        if g.get('position') == 'above':
            glory += 100
        result[cid] = glory
    return result


# Courtly skills (the modifier of Geniality applies to them) and the roll of each activity
COURTLY_SKILLS = ('compose', 'courtesy', 'dancing', 'falconry', 'flirting', 'gaming', 'heraldry', 'intrigue',
                  'orate', 'play', 'romance', 'singing', 'tourney')
ACTIVITY_SKILLS = {'gossip': 'intrigue', 'flirt': 'flirting', 'game': 'gaming'}   # Indulge: Temperate or Indulgent
FORCED_ACTIVITY = {'temperate': 'indulge', 'chaste': 'flirt'}   # what a failed first round requirement forces
RESULT_BY_CODE = {1: 'success', 2: 'critical', 3: 'fumble', 4: 'failure'}   # codes of utils.check2


def is_courtly(skill):
    return str(skill).lower().startswith(COURTLY_SKILLS)
