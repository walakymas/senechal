"""The feast API (Book of Feasts rules in feast_rules.py / feast.py).

Every call needs a valid session `token` (like `roll` and `command`). Players act with their own character
(player.did == the character's memberid), the host (admin right) with any, and only the host runs the feast itself.
Mutations are POSTs; the answer is the whole feast (the shape of `GET /feast`) plus what the call rolled.
"""
import copy
import functools
import json
import logging

from api.compat import JsonResponse, never_cache
from character import Character
from config import Config
from database.eventstable import EventsTable
from database.feasttable import FeastTable
from database.tokenstable import TokenTable
from feast import Feast
import feast_rules as rules
import permissions

log = logging.getLogger(__name__)

MAX_ROUNDS = 10


class ApiError(Exception):
    def __init__(self, status, text):
        super().__init__(text)
        self.status = status
        self.text = text


def _json(data, status=200):
    return JsonResponse(data, safe=False, status=status, json_dumps_params={'ensure_ascii': False})


def session(request):
    """The token record of a valid session (see TokenTable.get_info_by_token) or None."""
    token = request.POST.get('token') or request.GET.get('token')
    record = TokenTable().get_info_by_token(token) if token else None
    return record if record and record[5] == 1 else None


def is_admin(record):
    return bool(record[4]) and record[4] & permissions.ADMIN == permissions.ADMIN


def can_act_for(record, cid):
    """The host acts for everybody, a player for the characters he owns."""
    if is_admin(record):
        return True
    character = Character.get_by_id(cid)
    return character is not None and character.memberid is not None and str(character.memberid) == str(record[1])


def int_param(request, name, default=None, low=None, high=None):
    raw = request.POST.get(name)
    if raw is None or raw == '':
        if default is None:
            raise ApiError(400, f'Missing parameter: {name}')
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ApiError(400, f'{name} must be a number')
    if (low is not None and value < low) or (high is not None and value > high):
        raise ApiError(400, f'{name} is out of range')
    return value


def load_feast(request):
    """The feast of `fid`, by default the latest one."""
    fid = request.POST.get('fid') or request.GET.get('fid')
    try:
        record = FeastTable().get(int(fid)) if fid else FeastTable().get()
    except ValueError:
        raise ApiError(400, 'fid must be a number')
    if not record:
        raise ApiError(404, 'No such feast')
    return Feast(record)


def feast_json(f):
    """The feast as the API shows it: `enabled` lists the cards of the current round a guest may play."""
    data = copy.deepcopy(f.get_data())
    round = str(data['data'].get('round'))
    for guest in data['data']['participiants'].values():
        pround = guest.get('rounds', {}).get(round, {})
        guest['enabled'] = [c for c in pround.get('cards', [])
                            if 'selected' not in pround and Feast.card_enabled(c, pround, guest.get('significant', []))]
    return data


def roll(value, modifier=0):
    """A d20 roll against `value` + `modifier` (the rule of utils.check2: above 20 it adds to the roll)."""
    import utils  # imports discord: only when something is rolled
    color, text, total, die, code = utils.check2(value, modifier, emoji=False)
    return {'result': rules.RESULT_BY_CODE[code], 'roll': die, 'total': total, 'target': value + modifier}


def checkable_value(character, name):
    """The value of the first skill / trait / stat / passion of the character that starts with `name`."""
    from utils import get_checkable
    Config.senechal()
    found = next(iter(get_checkable(character.get_data(), name)), None)
    if found is None:
        raise ApiError(409, f'{character.name} has no {name}')
    return found[2]


def feast_view(role):
    """Wraps a feast call: session and rights (role 'admin' or 'player'), parameters, errors as JSON.
    The function gets (feast, character or None, session record, request) and returns the extra part of the answer."""
    def decorator(fn):
        @functools.wraps(fn)
        @never_cache
        def view(request):
            try:
                record = session(request)
                if record is None:
                    raise ApiError(403, 'Login needed')
                if role == 'admin' and not is_admin(record):
                    raise ApiError(403, 'Only the host can do this')
                f = None if getattr(fn, 'creates', False) else load_feast(request)
                character = None
                if role == 'player':
                    cid = int_param(request, 'cid')
                    if not can_act_for(record, cid):
                        raise ApiError(403, 'This is not your character')
                    character = Character.get_by_id(cid)
                    if character is None:
                        raise ApiError(404, 'No such character')
                extra = fn(f, character, record, request)
                if isinstance(extra, Feast):
                    f, extra = extra, None
                answer = feast_json(f)
                if extra:
                    answer['rolled'] = extra
                return _json(answer)
            except ApiError as ex:
                return _json({'error': ex.text}, ex.status)
        return view
    return decorator


def _guest(f, character):
    guest = f.data['participiants'].get(str(character.id))
    if guest is None:
        raise ApiError(404, f'{character.name} is not at the feast')
    return guest


def _round(f, guest):
    return guest['rounds'].get(str(f.data['round']), {})


def _in_feast(f):
    if f.data['state'] != 'feast':
        raise ApiError(409, 'The feast is not running')


@never_cache
def feasts(request):
    """The list of the feasts, the latest first."""
    result = []
    for r in FeastTable().list():
        try:
            data = json.loads(r[5])
        except (TypeError, ValueError):
            data = {}
        result.append({'id': r[0], 'created': r[1], 'title': r[3], 'state': data.get('state'),
                       'round': data.get('round'), 'rounds': data.get('rounds')})
    return _json(result)


@never_cache
def feast_get(request):
    """One feast (`fid`, default the latest); it never creates one."""
    try:
        return _json(feast_json(load_feast(request)))
    except ApiError as ex:
        return _json({'error': ex.text}, ex.status)


def _new(f, character, record, request):
    rounds = int_param(request, 'rounds', 3, 1, MAX_ROUNDS)
    feast = Feast(None)
    feast.title = request.POST.get('title', '')[:100]
    FeastTable().update(feast)
    feast.set_rounds(rounds)
    feast.set_royal(request.POST.get('royal') in ('1', 'true', 'True'))
    return feast


_new.creates = True
feast_new = feast_view('admin')(_new)


@feast_view('admin')
def feast_next(f, character, record, request):
    f.next_state()


@feast_view('admin')
def feast_seat(f, character, record, request):
    """The host seats a guest by hand."""
    cid = int_param(request, 'cid')
    seat = request.POST.get('seat')
    if seat not in rules.SEATS:
        raise ApiError(400, 'seat must be one of ' + ', '.join(rules.SEATS))
    if f.data['state'] != 'init':
        raise ApiError(409, 'Guests can only be seated before the feast')
    if Character.get_by_id(cid) is None:
        raise ApiError(404, 'No such character')
    f.add_participiant(cid)
    f.set_participiant(cid, seat, EventsTable().glory(cid))


@feast_view('player')
def feast_app_roll(f, character, record, request):
    """The APP roll before the feast: the guest is added and seated by the result (once, unless the host repeats it)."""
    if f.data['state'] != 'init':
        raise ApiError(409, 'The APP roll is made before the feast')
    existing = f.data['participiants'].get(str(character.id))
    if existing is not None and 'app' in existing and not is_admin(record):
        raise ApiError(409, 'The APP roll is already made')
    base = int(character.data['stats']['app'])
    bonus = rules.app_bonus(int_param(request, 'jewelry', 0, 0, 100), int_param(request, 'fashion', 0, 0, 100)) \
        if request.POST.get('jewelry') or request.POST.get('fashion') else 0
    first = roll(base, bonus)
    second = roll(base, bonus) if first['result'] == 'fumble' else None
    f.add_participiant(character.id)
    position = f.seat_by_app(character.id, first['result'], second['result'] if second else None,
                             app=(second or first)['total'])
    f.set_participiant(character.id, position, EventsTable().glory(character.id))
    return {'first': first, 'second': second, 'position': position}


@feast_view('player')
def feast_activity(f, character, record, request):
    """The activity of the round: card, gossip, indulge, flirt, game (or pass)."""
    _in_feast(f)
    activity = request.POST.get('activity')
    if activity not in rules.ACTIVITIES:
        raise ApiError(400, 'activity must be one of ' + ', '.join(rules.ACTIVITIES))
    guest = _guest(f, character)
    if guest.get('left'):
        raise ApiError(409, f'{character.name} has left the feast')
    if 'action' in _round(f, guest):
        raise ApiError(409, 'The activity of this round is already chosen')
    f.set_round_action(activity, character.id)
    if _round(f, guest).get('action') != activity:
        raise ApiError(409, 'This activity is not allowed (feast cards need 1,000 Glory and a seat below the salt)')


@feast_view('player')
def feast_requirement(f, character, record, request):
    """Round 1: the Temperate / Chaste roll a guest with an Indulgent / Lustful of 16+ needs to do something else."""
    _in_feast(f)
    guest = _guest(f, character)
    trait = request.POST.get('trait')
    if trait not in _round(f, guest).get('requires', []):
        raise ApiError(409, 'No such requirement')
    rolled = roll(checkable_value(character, trait))
    f.resolve_requirement(character.id, trait, rolled['result'])
    return rolled


@feast_view('player')
def feast_roll(f, character, record, request):
    """The roll of a Gossip / Indulge / Flirt / Game round (Intrigue / Temperate or Indulgent / Flirting / Gaming)."""
    _in_feast(f)
    guest = _guest(f, character)
    pround = _round(f, guest)
    activity = pround.get('action')
    if activity not in ('gossip', 'indulge', 'flirt', 'game') or pround.get('requires') or 'result' in pround:
        raise ApiError(409, 'There is nothing to roll')
    if activity == 'indulge':
        skill = request.POST.get('trait', 'temperate')
        if skill not in ('temperate', 'indulgent'):
            raise ApiError(400, 'trait must be temperate or indulgent')
    else:
        skill = rules.ACTIVITY_SKILLS[activity]
    modifier = rules.clamp_geniality_modifier(guest['geniality']) if rules.is_courtly(skill) else 0
    rolled = roll(checkable_value(character, skill), modifier)
    f.record_result(character.id, rolled['result'])
    return rolled


@feast_view('player')
def feast_select_card(f, character, record, request):
    """Plays a card of the hand (Host and Mandatory cards come first, see Feast.card_enabled)."""
    _in_feast(f)
    guest = _guest(f, character)
    card = int_param(request, 'card')
    if 'selected' in _round(f, guest):
        raise ApiError(409, 'A card is already played in this round')
    f.select_card(character.id, card)
    if _round(f, guest).get('selected') != card:
        raise ApiError(409, 'This card cannot be played')


@feast_view('player')
def feast_discard_kept(f, character, record, request):
    if not f.discard_kept(character.id, int_param(request, 'card')):
        raise ApiError(409, 'No such kept card')


@feast_view('player')
def feast_leave(f, character, record, request):
    """Leaving the feast: with `voluntary` the Courtesy roll is made, otherwise the departure is forced."""
    _in_feast(f)
    _guest(f, character)
    rolled = None
    if request.POST.get('voluntary') in ('1', 'true', 'True'):
        guest = f.data['participiants'][str(character.id)]
        if f.data['round'] < 2:
            raise ApiError(409, 'The first round has to be attended')
        rolled = roll(checkable_value(character, 'courtesy'), rules.clamp_geniality_modifier(guest['geniality']))
    if not f.leave(character.id, rolled['result'] if rolled else None):
        raise ApiError(409, 'Already left')
    return rolled


@feast_view('player')
def feast_return(f, character, record, request):
    _in_feast(f)
    if not f.return_to_feast(character.id):
        raise ApiError(409, 'Not away from the feast')
