import json
import os
import re
from json import JSONDecodeError

from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.cache import never_cache

from character import Character
from database.charactertable import CharacterTable
from database.markstable import MarksTable
from database.eventstable import EventsTable
from datetime import datetime
import tempfile


def index(request):
    return HttpResponse("Hello, world. You're at the senechal index.")


def base(request):
    from config import Config
    result = Config.senechal()
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

def pcresponse(pc):
    data = {'char': pc.get_data(False), 'modified':datetime.timestamp(pc.modified)}
    year = MarksTable().year()
    data['year'] = year
    if 'memberId' in data['char']:
        data['char']['memberId'] = str(data['char']['memberId'])
        data['marks'] = []
        for r in MarksTable().list(data['char']['memberId'], year):
            data['marks'].append(r[5])
        data['events'] = []
        for r in EventsTable().list(data['char']['memberId']):
            data['events'].append({'year': r[3], 'description': r[5], 'glory': r[6], 'id': r[0]})
    s = json.dumps(data, indent=4, ensure_ascii=False)
    response = HttpResponse(s)
    response['Content-Type'] = 'application/json'
    return response

@never_cache
def pcs(request):
    result = []
    records = CharacterTable().get_pcs()
    for r in records:
        c = Character(r)
        if not ('role' in c.data and (c.data['role'] == 'Lord' or c.data['role'] == 'King' or c.data['role'] == 'Retired' )):
            result.append(c.get_data())
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})


def list(request):
    chars = []
    for ch in CharacterTable().list():
        type = 'npc'
        if ch[3]:
            type = 'pc'
        chars.append({'id': ch[0], 'modified': ch[2], 'name': ch[4], 'type': type, 'role': ch[7]})
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


def mark(request):
    mid = request.POST['id']
    year = int(MarksTable.year())
    if 'set' in request.POST and request.POST['set']=='false':
        MarksTable().remove_by_name(mid, year, request.POST['mark'])
    else:
        MarksTable().set(mid, year, request.POST['mark'])
    return pcresponse(Character.get_by_memberid(mid, True))


def event(request):
    eid = int(request.POST['eid'])
    glory = int(request.POST['glory'])
    mid = int(request.POST['mid'])
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
            EventsTable().insert(mid, description, glory, year)
    return pcresponse(Character.get_by_memberid(mid, True))


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
    if 'json' in request.POST:
        CharacterTable().set_json(request.POST['id'], request.POST['json'])
    else:
        j = CharacterTable().get_by_id(request.POST['id'])[6]
        data = json.loads(j)
        for name, value in request.POST.items():
            if "id" != name:
                set(data, name, value)
        j = json.dumps(data, ensure_ascii=False, indent=2)
        CharacterTable().set_json(request.POST['id'], j)
    return pcresponse(Character.get_by_id(request.POST['id'], force=True))


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
