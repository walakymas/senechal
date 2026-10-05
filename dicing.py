import re

from utils import dice

# '4d20', 'd6', '2d6+3' (the same format as the !4d20 command)
dicePattern = re.compile('([0-9]*)[dD]([0-9]+)([+-][0-9]+)?')


def roll_dice(count, size, modifier=None):
    """Rolls `count`d`size` (+/- modifier). Returns (text like '3+5= 8', result json for the checks table)."""
    num = int(count) if '' != count else 1
    toJson = {'action': 'dice'}
    c = {'count': count, 'size': size, 'dices': []}
    toJson['c1'] = c
    total = 0
    s = ''
    for x in range(num):
        r = dice(int(size))
        c['dices'].append(r)
        total += r
        if x > 0:
            s += '+'
        s += str(r)
    if modifier:
        total += int(modifier)
        s += modifier
        c['modifier'] = int(modifier)
    c['sum'] = total
    return s + '= ' + str(total), toJson
