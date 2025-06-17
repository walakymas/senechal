import json
import os
import re
import uuid;
from json import JSONDecodeError

from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.cache import never_cache

from character import Character
from database.charactertable import CharacterTable
from database.playertable import PlayerTable
from database.markstable import MarksTable
from database.eventstable import EventsTable
from database.tokenstable import TokenTable
from database.checktable import CheckTable
from database.base_table_handler import BaseTableHandler
from datetime import datetime
import tempfile
from config import Config
import zipfile

def index(request):
    return HttpResponse("Hello, world. You're at the senechal index.")


def base(request):

    result = Config.senechal()
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

def pcresponse(pc):
    data = {'char': pc.get_data(False), 'modified':datetime.timestamp(pc.modified)}
    year = MarksTable().year()
    data['year'] = year
    if 'memberId' in data['char']:
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
    glorys = EventsTable().glorys();    
    records = CharacterTable().get_pcs()
    
    for r in records:
        c = Character(r)
        d = c.get_data()
        if not ('role' in c.data and (c.data['role'] == 'Lord' or c.data['role'] == 'King' or c.data['role'] == 'Retired' )):
            for g in glorys:
                print(f'{g}')
                if g[0] == c.id:
                    d['Glory']=g[1]
            result.append(d)
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

def user(request):
    token = request.POST['token']
    resp = {'result':'fail'}
    record = TokenTable().get_info_by_token(token)
    if record:
        if record[5]==1:
            resp = {'name':record[6], 'id':record[7], 'expires':record[2], 'rights':record[4]}
    return JsonResponse(resp, safe=False, json_dumps_params={'ensure_ascii': False})
    
def token(request):
    cid = request.POST['cid']
    resp = {'result':'fail'}
    plyr = PlayerTable().get_by_cid(cid)
    if plyr:
        token = f"{uuid.uuid4()}"
        try:
            print(plyr)
            TokenTable().set(token, plyr[0], None, 0)
            record = TokenTable().get_info_by_token(token)
            resp = {'result':'fail'}
            if record:
                resp = {'token':token, 'id':record[0], 'rights':record[4]}
            
        except BaseException as ex:
            print(ex)
            return JsonResponse({'error':ex}, safe=False, json_dumps_params={'ensure_ascii': False})
    else:
        print(f"plyr failed")

    return JsonResponse(resp, safe=False, json_dumps_params={'ensure_ascii': False})

def list(request):
    chars = []
    for ch in CharacterTable().list():
        type = 'npc'
        if ch[3]:
            type = 'pc'
        chars.append({'id': ch[0], 'modified': ch[2], 'name': ch[4], 'type': type, 'role': ch[7], 'player': ch[8], 'url': ch[5], 'memberid':str(ch[3])})
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
    for ch in CharacterTable().list():
        names[ch[4]] = ch[0]
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
            print(f'{name} : {value}')
            try:
                data[name] = json.loads(value)
            except JSONDecodeError:
                data[name] = value
        else:
            dn = name[0:i]
            if dn not in data:
                data[dn] = {}
            set(data[dn], name[i+1:], value)
    if 'token' in  request.POST:
        if hasRight(request.POST['token'], request.POST['id']):
            if 'json' in request.POST:
                CharacterTable().set_json(request.POST['id'], request.POST['json'])
            else:
                j = CharacterTable().get_by_id(request.POST['id'])[6]
                data = json.loads(j)
                for name, value in request.POST.items():
                    if "id" != name and "token" != name:
                        set(data, name, value)
                j = json.dumps(data, ensure_ascii=False, indent=2)
                CharacterTable().set_json(request.POST['id'], j)
        else:
            print("modification prohibited")
    return pcresponse(Character.get_by_id(request.POST['id'], force=True))

def hasRight(token, cid):
    print(f"to: {token}")
    return token != 'null'

def pdfs(request):
    fz = os.path.join(tempfile.gettempdir(), str(next(tempfile._get_candidate_names()))+"_tmp.pdf")
    zf = zipfile.ZipFile(fz, "w")
    from pdf.sheet import Sheet
    for ch in CharacterTable().list():
        if ch[3]:
            pc = Character.get_by_id(ch[0])
            sheet = Sheet(pc)
            fp = os.path.join(tempfile.gettempdir(), str(next(tempfile._get_candidate_names()))+"_tmp.pdf")
            print(fp)
            sheet.output(fp, 'F')
            zf.write(fp,f"{pc.name}.pdf")
    zf.close()
    response = FileResponse(open(fz, 'rb'), filename=f"teampdf.zip")
    response['Content-Type'] = 'application/zip'
    return response


def pdf(request):
    if 'id' in request.GET:
        pc = Character.get_by_id(request.GET['id'])
        if pc:
            from pdf.sheet import Sheet
            sheet = Sheet(pc)
            fp = os.path.join(tempfile.gettempdir(), str(next(tempfile._get_candidate_names()))+"_tmp.pdf")
            print(fp)
            sheet.output(fp, 'F')
            response = FileResponse(open(fp, 'rb'), filename=f"{pc.name}.pdf")
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
    ('did','string'),
    ('name','string'),
    ('character','number')
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
    return JsonResponse(convert(list, fields), safe=False, json_dumps_params={'ensure_ascii': False})

def convert(list, fields):
    result = []
    for l in list:
        i = 0
        row = {}
        for f in fields:
            if f[1]=='json':
                print(f"{f} {f[0]} {i} {l}")
                ll = l[i].replace('\\n','\n')
                print(f"{ll}")
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
    print(p)
    return JsonResponse(p, safe=False, json_dumps_params={'ensure_ascii': False})

def cleanupTokens(request):
    BaseTableHandler.execute(
        "DELETE FROM tokens expires < NOW() - INTERVALL '1 DAYS'", request.POST, commit=True)
    return JsonResponse(convert(TokenTable().list(), TOKEN_FIELDS), safe=False, json_dumps_params={'ensure_ascii': False})

def checks(request):
    result = []
    res = CheckTable().list()
    for i in res:
        print(f"{i}")
        result.append(convert(i,CHECK_FIELDS)) 
    return JsonResponse(convert(res,CHECK_FIELDS), safe=False, json_dumps_params={'ensure_ascii': False})
