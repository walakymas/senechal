import io
import json
import logging
import os
import re
import threading
import time
import uuid;
from urllib.parse import urlparse
from json import JSONDecodeError

from api.compat import HttpResponse, JsonResponse, FileResponse
from api.compat import never_cache

from character import Character, ensure_economy
from database.c2ctable import C2CTable
from database.charactertable import CharacterTable
from database.playertable import PlayerTable
from database.markstable import MarksTable
from database.eventstable import EventsTable
from database.tokenstable import TokenTable
from database.checktable import CheckTable
from database.base_table_handler import BaseTableHandler
from database.feasttable import FeastTable
from database.proptable import PropertiesTable
from database.mapstable import MapsTable  

from feast import Feast
from datetime import datetime
import tempfile
from config import Config
import zipfile

log = logging.getLogger(__name__)


MAP_FIELDS = [
    ('id','number'),
    ('created','string'),
    ('modified','string'),
    ('url','string'),
    ('category','string'),
    ('ord','number'),
    ('name','string')
]

def index(request):
    return HttpResponse("Hello, world. You're at the senechal index.")


def base(request):
    result = Config.senechal()
    if Config.authorization:
        result['loginNeeded'] = 'true'
    result['hook'] = Config.hook
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

def pcresponse(pc):
    data = {'char': pc.get_data(False), 'modified':datetime.timestamp(pc.modified)}
    year = MarksTable().year()
    data['year'] = year
    if data['char'].get('memberId') is not None:
        data['char']['memberId'] = str(data['char']['memberId'])
    data['events'] = []
    for r in EventsTable().list(data['char']['dbid']):
        data['events'].append({'year': r[3], 'description': r[5], 'glory': r[6], 'id': r[0]})
    data['marks'] = []
    for r in MarksTable().list(data['char']['dbid'], year):
        data['marks'].append(r[5])
    senechal = Config.senechal()
    data['virtues'] = senechal['virtues']['British Christian']
    if 'main' in data['char']:
        if 'Religion' in data['char']['main']:
            data['virtues'] = senechal['virtues'][data['char']['main']['Religion']]
        elif 'Culture' in data['char']['main']:
            found = False 
            for r in  senechal['virtues'].keys():
                if r in data['char']['main']['Culture']:
                    data['virtues'] = senechal['virtues'][r]
                    found = True
            if not found and 'Pagan' in  data['char']['main']['Culture']:
                data['virtues'] = senechal['virtues']['British Pagan']
    s = json.dumps(data, indent=4, ensure_ascii=False)
    response = HttpResponse(s)
    response['Content-Type'] = 'application/json'
    return response

@never_cache
def pcs(request):
    result = []
    glorys = dict(EventsTable().glorys())  # {dbid: glory sum}
    records = CharacterTable().get_pcs()
    
    for r in records:
        c = Character(r)
        d = c.get_data()
        if not ('role' in c.data and (c.data['role'] == 'Lord' or c.data['role'] == 'King' or c.data['role'] == 'Retired' )):
            if c.id in glorys:
                d['Glory'] = glorys[c.id]
            result.append(d)
        if c.data.get('memberId') is not None:
            c.data['memberId'] = str(c.data['memberId'])

    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

def user(request):
    token = request.POST['token']
    resp = {'result':'fail'}
    record = TokenTable().get_info_by_token(token)
    if record:
        if record[5]==1:
            resp = {'name':record[6], 'id':record[7], 'expires':record[2], 'rights':record[4], 'did':str(record[1])}
    return JsonResponse(resp, safe=False, json_dumps_params={'ensure_ascii': False})
    
def token(request):
    cid = request.POST['cid']
    resp = {'result':'fail'}
    plyr = PlayerTable().get_by_cid(cid)
    if plyr:
        token = f"{uuid.uuid4()}"
        try:
            TokenTable().set(token, plyr[0], None, 0)
            record = TokenTable().get_info_by_token(token)
            resp = {'result':'fail'}
            if record:
                resp = {'token':token, 'id':record[0], 'rights':record[4]}
            
        except BaseException as ex:
            log.warning("token: %s", ex)
            return JsonResponse({'error':ex}, safe=False, json_dumps_params={'ensure_ascii': False})
    else:
        log.debug("token: unknown player")

    return JsonResponse(resp, safe=False, json_dumps_params={'ensure_ascii': False})

def list(request):
    chars = []
    for ch in CharacterTable().list_summary():  # id, modified, name, url, role, player, pmid
        type = 'npc'
        if ch[6]:
            type = 'pc'
        chars.append({'id': ch[0], 'modified': ch[1], 'name': ch[2], 'type': type, 'role': ch[4], 'player': ch[5], 'url': ch[3], 'memberid':str(ch[6])})
    return JsonResponse(chars, safe=False, json_dumps_params={'ensure_ascii': False})

@never_cache
def get_character(request):
    pc = None
    if 'id' in request.GET:
        pc = Character.get_by_id(request.GET['id'], force=True)
    elif 'ch' in request.GET:
        pc = Character.get_by_name(request.GET['ch'], force=True)
    if pc:
        return pcresponse(pc)
    names = {}
    for ch in CharacterTable().list_summary():
        names[ch[2]] = ch[0]
    return JsonResponse(names, safe=False, json_dumps_params={'ensure_ascii': False})


@never_cache
def npc(request):
    return pcresponse(Character.get_by_id(request.GET['id'], force=True))

@never_cache
def login(request):
    data = {}    
    s = json.dumps(data, indent=4, ensure_ascii=False)
    response = HttpResponse(s)
    response['Content-Type'] = 'application/json'
    return response
    

def mark(request):
    id = request.POST['id']
    year = int(MarksTable.year())
    if 'set' in request.POST and request.POST['set']=='false':
        MarksTable().remove_by_name(id, year, request.POST['mark'])
    else:
        MarksTable().set(id, year, request.POST['mark'])
    return pcresponse(Character.get_by_id(id, True))

def event(request):
    eid = int(request.POST['eid'])
    glory = int(request.POST['glory'])
    id = int(request.POST['dbid'])
    if eid > 0 and glory < 0:
        EventsTable().remove(eid)
    else:
        year = int(request.POST['year'])
        if year <= 0:
            year = int(MarksTable.year())
        description = request.POST['description']
        if eid > 0:
            EventsTable().update(eid, description, glory, year)
        else:
            EventsTable().insert(id, description, glory, year)
    return pcresponse(Character.get_by_id(id, True))


def newchar(request):
    CharacterTable().add(request.POST['json'])
    data = json.loads(request.POST['json'])
    return pcresponse(Character.get_by_name(data['name']))


def modify(request):
    def set(data, name, value):
        i = name.find('.')
        if name in data or i < 0:
            log.debug("modify field %s", name)
            try:
                data[name] = json.loads(value)
            except JSONDecodeError:
                data[name] = value
        else:
            dn = name[0:i]
            if dn not in data:
                data[dn] = {}
            set(data[dn], name[i+1:], value)
    if not(Config.authorization) or (('token' in  request.POST and hasRight(request.POST['token'], request.POST['id']))):
        log.debug("modify")
        if 'json' in request.POST:
            CharacterTable().set_json(request.POST['id'], request.POST['json'])
        else:
            j = CharacterTable().get_by_id(request.POST['id'])[6]
            data = ensure_economy(json.loads(j))
            for name, value in request.POST.items():
                if "id" != name and "token" != name:
                    log.debug("modify field %s", name)
                    set(data, name, value)
            j = json.dumps(data, ensure_ascii=False, indent=2)
            CharacterTable().set_json(request.POST['id'], j)
    else:
        log.warning("modification prohibited")
    return pcresponse(Character.get_by_id(request.POST['id'], force=True))

def _discord_channel(record):
    """Channel for the user's messages: `<prefix>channel<player id>`, else `<prefix>channel`, else the main channel."""
    for key in (f"{Config.prefix}channel{record[7]}", f"{Config.prefix}channel"):
        row = PropertiesTable().get(key)
        if row and row[3]:
            return row[3]
    return Config.mainChannel.id if Config.mainChannel is not None else None


def _send_to_discord(action, *args):
    try:
        return action(*args)
    except BaseException as ex:
        log.warning("discord send failed: %s", ex)
        return False


def roll(request):
    """Dice roll from the character page, shown in Discord as if the '!4d20' command was typed."""
    import bot_bridge
    from dicing import dicePattern, roll_dice
    record = TokenTable().get_info_by_token(request.POST['token'])
    if not record or record[5] != 1:
        return JsonResponse({'result': 'fail'}, status=403)
    spec = request.POST['dice'].strip()
    m = dicePattern.fullmatch(spec)
    if not m or int(m.group(1) or 1) > 100 or int(m.group(2)) < 1 or int(m.group(2)) > 1000:
        return JsonResponse({'result': 'fail'}, status=400)
    text, result = roll_dice(*m.groups())
    name = record[6]
    if request.POST.get('id'):
        result['char'] = int(request.POST['id'])
        CheckTable().add(character=result['char'], command=Config.prefix + spec,
                         result=json.dumps(result, indent=4, ensure_ascii=False))
        char = Character.get_by_id(result['char'])
        if char:
            name = char.name
    channel_id = _discord_channel(record)
    sent = channel_id is not None and _send_to_discord(
        bot_bridge.send, channel_id, f"{name} (`{Config.prefix}{spec}`): {text}")
    return JsonResponse({'result': 'ok' if sent else 'not sent', 'text': text}, safe=False,
                        json_dumps_params={'ensure_ascii': False})


# Commands the web page may run (by command name); anything else (db, admin, ...) is refused
WEB_COMMANDS = ('check', 'team')


def command(request):
    """Runs a bot command from the web page in the user's channel, instead of posting it through a webhook.
    `command` is the text without the prefix, e.g. 'c Sword 0 cid:5'."""
    import bot_bridge
    import message_handler
    record = TokenTable().get_info_by_token(request.POST['token'])
    if not record or record[5] != 1:
        return JsonResponse({'result': 'fail'}, status=403)
    text = request.POST['command'].strip()
    handler = message_handler.COMMAND_ALIASES.get(text.split(' ')[0].lower()) if text else None
    if handler is None or handler.name not in WEB_COMMANDS:
        return JsonResponse({'result': 'refused'}, status=400)
    channel_id = _discord_channel(record)
    sent = channel_id is not None and _send_to_discord(
        bot_bridge.run_command, channel_id, Config.prefix + text, record[1], record[6])
    return JsonResponse({'result': 'ok' if sent else 'not sent'}, safe=False)


def hasRight(token, cid):
    return token != 'null'

# The team PDF (one sheet per player character) is slow to build: only one build runs at a time and the
# result is reused for PDFS_TTL seconds, so repeated requests cannot pile up work.
PDFS_TTL = 30
_pdfs_lock = threading.Lock()
_pdfs_cache = {'built': 0.0, 'data': None}
_FILE_NAME_BAD = dict.fromkeys([ord(c) for c in '/' + chr(92) + ':*?"<>|'] + [*range(32)], '_')  # (list is a view here)


def _team_zip():
    from pdf.sheet import Sheet
    team = {}
    for record in CharacterTable().get_pcs():  # the characters that have a player
        if record[0] not in team:
            team[record[0]] = Character(record)
    year = MarksTable().year()
    marks = MarksTable().list_for(team.keys(), year)
    events = EventsTable().list_by_dbid()
    glorys = {dbid: int(total or 0) for dbid, total in EventsTable().glorys()}
    buffer = io.BytesIO()
    names = set()
    with zipfile.ZipFile(buffer, "w") as zf:
        for pc in team.values():
            name = pc.name.translate(_FILE_NAME_BAD)
            if name in names:
                name = f"{name} ({pc.id})"
            names.add(name)
            sheet = Sheet(pc, year, marks.get(pc.id, []), events.get(pc.id, []), glorys.get(pc.id, 0))
            zf.writestr(f"{name}.pdf", bytes(sheet.output()))
    return buffer.getvalue()


def pdfs(request):
    with _pdfs_lock:
        if _pdfs_cache['data'] is None or time.monotonic() - _pdfs_cache['built'] > PDFS_TTL:
            _pdfs_cache['data'] = _team_zip()
            _pdfs_cache['built'] = time.monotonic()
        data = _pdfs_cache['data']
    response = FileResponse(io.BytesIO(data), filename="teampdf.zip")
    response['Content-Type'] = 'application/zip'
    return response


def pdf(request):
    if 'id' in request.GET:
        pc = Character.get_by_id(request.GET['id'])
        if pc:
            from pdf.sheet import Sheet
            sheet = Sheet(pc)
            response = FileResponse(io.BytesIO(bytes(sheet.output())), filename=f"{pc.name}.pdf")
            response['Content-Type'] = 'application/pdf'
            return response
        else:
            return HttpResponse(f"Nem találom: '{request.GET['id']}")
    else:
        return HttpResponse(f"Hiányzó paraméter: 'ch'")
PLAYER_FIELDS =  [
    ('cid','number'),
    ('created','string'),
    ('modified','string'),
    ('playerstate',''),
    ('playerrights','number'),
    ('name','string'),
    ('character','string'),
    ('memberid','number'),
    ('did','number')
    ]
TOKEN_FIELDS =  [
    ('id','number'),
    ('created','string'),
    ('modified','string'),
    ('expires','string'),
    ('cid','number'),
    ('token','number'),
    ('tokenstate','string')
    ]
CHECK_FIELDS =  [
    ('id','number'),
    ('created','string'),
    ('modified','string'),
    ('character','number'),
    ('command','string'),
    ('result','json'),
    ('name','string')
    ]
C2C_FIELDS =  [
    ('id','number'),
    ('created','string'),
    ('modified','string'),
    ('c0','number'),
    ('c1','number'),
    ('connection','string'),
    ('comment','string')
    ]
@never_cache
def adminList(request):
    list =  []
    fields = [('')]
    if request.GET['table']:
        if "player" == request.GET['table']:
            fields = PLAYER_FIELDS
            list = PlayerTable().list()
        elif "tokens" == request.GET['table']:
            fields = TOKEN_FIELDS
            list = TokenTable().list()
        elif "checks" == request.GET['table']:
            fields = CHECK_FIELDS
            list = CheckTable().list()
        elif "c2c" == request.GET['table']:
            fields = C2C_FIELDS
            list = C2CTable().list()
    return JsonResponse(convert(list, fields), safe=False, json_dumps_params={'ensure_ascii': False})

def convert(list, fields):
    result = []
    for l in list:
        i = 0
        row = {}
        for f in fields:
            if f[1]=='json':
                ll = l[i].replace('\\n','\n')
                row[f[0]]= json.loads(ll)
            else:
                row[f[0]]= str(l[i])
            i += 1
        result.append(row)
    return result

def updatePlayer(request):
    p = {}
    for i in request.POST:
        p[i]=request.POST[i]
    p['did']=int(p['did'])
    BaseTableHandler.execute(
        'UPDATE player SET name=%(name)s,character=%(character)s,did=%(did)s  WHERE cid=%(cid)s', request.POST, commit=True)
    p = convert([PlayerTable().get(request.POST['cid'])], PLAYER_FIELDS)[0]
    p['did']=f"{p['did']}"
    return JsonResponse(p, safe=False, json_dumps_params={'ensure_ascii': False})

def cleanupTokens(request):
    BaseTableHandler.execute(
        "DELETE FROM tokens WHERE expires < NOW() - INTERVAL '1 DAYS'", commit=True)
    return JsonResponse(convert(TokenTable().list(), TOKEN_FIELDS), safe=False, json_dumps_params={'ensure_ascii': False})

def checks(request):
    result = []
    res = CheckTable().list(limit=10)
    return JsonResponse(convert(res,CHECK_FIELDS), safe=False, json_dumps_params={'ensure_ascii': False})

def addC2C(request):
    C2CTable().add(request.POST['c0']*1, request.POST['c1']*1, request.POST['connection'], request.POST['comment'])
    fields = C2C_FIELDS
    list = C2CTable().list()
    if request.POST['withchars'] == 'true':
        return connectionsByCid(request.POST['c0']*1)
    else:
        return JsonResponse(convert(list, fields), safe=False, json_dumps_params={'ensure_ascii': False})


def connections(request):
    cid = request.GET['cid']
    return connectionsByCid(cid)

def connectionsByCid(cid):
    list = convert(C2CTable().list(cid), C2C_FIELDS)
    year = MarksTable().year()
    cid = str(cid)  # convert() turns every field into text, so c0 / c1 are compared with the id as text
    others = [c2c['c1'] if c2c['c0'] == cid else c2c['c0'] for c2c in list]
    chars = Character.get_many_by_id(others)          # one query for all the other characters ...
    marks = MarksTable().list_for(chars.keys(), year)  # ... and one for their marks
    for c2c, c in zip(list, others):
        pc = chars.get(int(c))
        if pc:
            c2c['char'] = pc.get_data()
            c2c['marks'] = marks.get(int(c), [])[:]
        else:
            c2c['char'] = None

    return JsonResponse(list, safe=False, json_dumps_params={'ensure_ascii': False})

def feastConfig(request):
    result = Config.feast()
    if Config.authorization:
        result['loginNeeded'] = 'true';
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False}) 
 
@never_cache
def feast(request):
    feast = FeastTable().get()
    if feast:
        f = Feast(feast)
    else:
        f = Feast(None)
        feast = FeastTable().get()
        f = Feast(feast)
    if( hasattr(request, 'POST') and 'action' in request.POST):
        log.debug("feast action %s", request.POST['action'])
        action = request.POST['action']
        if action == 'test':
            f.data['state'] = 'init'
            f.set_rounds(4)
            f.set_courses(['Appetizer', 'Soup','Main Course', 'Dessert'])
            f.add_participiant(36)
            f.add_participiant(71)
            f.add_participiant(37)
            f.add_participiant(32)
            f.set_participiant(36, 'near', EventsTable().glory(36))
            f.set_participiant(37, 'above', EventsTable().glory(37))
            f.set_participiant(32, 'near', EventsTable().glory(32))
            f.set_participiant(71, 'below', EventsTable().glory(71))
            f.data['round'] = 1
            f.draw_card(36)
            f.draw_card(71)
            f.draw_card(37)
            f.draw_card(32)
        elif action == 'seat':
            if 'cid' in request.POST:
                cid = int(request.POST['cid'])
                f.add_participiant(cid)
                f.set_participiant(cid, request.POST['seat'], EventsTable().glory(cid))
        elif action == 'setrounds':
            if 'rounds' in request.POST:
                f.data['rounds'] = int(request.POST['rounds'])
                FeastTable().updateData(f);
        elif action == 'setcourses':
            if 'courses' in request.POST:
                f.set_courses(request.POST['courses'].split(','))
        elif action == 'nextState':
            f.next_state()
        elif action == 'roundAction':
            if 'roundAction' in request.POST and 'pid' in request.POST:
                f.set_round_action(request.POST['roundAction'], int(request.POST['pid']))


    data = f.get_data()
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

@never_cache
def maps(request):
     # Return all available maps
    list = MapsTable().list()
    return JsonResponse(convert(list, MAP_FIELDS), safe=False, json_dumps_params={'ensure_ascii': False})


def is_http_url(url):
    """Only absolute http(s) addresses are stored for the maps (no javascript:, data:, file: ...)."""
    parsed = urlparse(url or '')
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)


def add_map(request):
    # expects POST with url, category, ord, name
    try:
        url = request.POST['url']
        if not is_http_url(url):
            return JsonResponse({'error': 'url must be an http(s) address'}, status=400)
        category = request.POST.get('category','')
        ord = int(request.POST.get('ord','0'))
        name = request.POST.get('name','')
        MapsTable().add(url, category, ord, name)
        return maps(request)
    except Exception as ex:
        return JsonResponse({'error':str(ex)}, safe=False, json_dumps_params={'ensure_ascii': False})


def update_map(request):
    # expects POST with id, url, category, ord, name
    try:
        id = int(request.POST['id'])
        url = request.POST['url']
        if not is_http_url(url):
            return JsonResponse({'error': 'url must be an http(s) address'}, status=400)
        category = request.POST.get('category','')
        ord = int(request.POST.get('ord','0'))
        name = request.POST.get('name','')
        MapsTable().update(id, url, category, ord, name)
        return maps(request)
    except Exception as ex:
        return JsonResponse({'error':str(ex)}, safe=False, json_dumps_params={'ensure_ascii': False})


def delete_map(request):
    # expects GET or POST with id
    try:
        id = int(request.POST.get('id', request.GET.get('id')))
        MapsTable().remove(id)
        return maps(request)
    except Exception as ex:
        return JsonResponse({'error':str(ex)}, safe=False, json_dumps_params={'ensure_ascii': False})
