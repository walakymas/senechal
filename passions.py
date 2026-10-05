import re

# Passion categories (display order). A passion's category is derived from the first
# word of its name; the stored name itself is never changed.
OTHER = 'Other'
PASSION_CATEGORIES = {
    'Fidelitas': ['duty', 'fealty', 'homage', 'loyalty'],
    'Fervor': ['hate', 'love'],
    'Adoratio': ['adoration', 'devotion'],
    'Civilitas': ['chivalry', 'hospitality', 'station'],
}
# Misspellings / variants found in existing data -> canonical first word
# (Honor is deliberately not a category member: it is shown among the 'Other' passions)
PASSION_ALIASES = {
    'fealthy': 'fealty',
    'hospitability': 'hospitality',
    'amor': 'adoration',
}
PASSION_WARN_TOTAL = 40  # a category total above this is highlighted
_FIRST_WORD = re.compile(r'\s*([A-Za-z]+)')


def passion_category(name):
    m = _FIRST_WORD.match(name)
    if m:
        word = m.group(1).lower()
        word = PASSION_ALIASES.get(word, word)
        for category, types in PASSION_CATEGORIES.items():
            if word in types:
                return category
    return OTHER


def group_passions(passions):
    """Returns [(category, [(name, int value), ...]), ...] with 'Other' first, then the
    categories in order, skipping empty ones; names are sorted within a category."""
    groups = {c: [] for c in [OTHER, *PASSION_CATEGORIES]}
    for name, value in passions.items():
        try:
            value = int(value)
        except (TypeError, ValueError):
            pass
        groups[passion_category(name)].append((name, value))
    return [(c, sorted(items, key=lambda i: i[0])) for c, items in groups.items() if items]


def passion_total(items):
    """Sum of the numeric values of [(name, value), ...]."""
    return sum(v for _, v in items if isinstance(v, int))
