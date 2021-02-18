import json

from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.cache import never_cache

from character import Character
from database.charactertable import CharacterTable
from database.markstable import MarksTable


def index(request):
    return HttpResponse("Hello, world. You're at the senechal index.")


@never_cache
def get_character(request):
    pc = None
    if 'id' in request.GET:
        pc = Character.get_by_id(request.GET['id'], force=True)
    elif 'ch' in request.GET:
        pc = Character.get_by_name(request.GET['ch'], force=True)
    if pc:
        data = {'char': pc.get_data(False)}
        if 'memberId' in data['char']:
            data['char']['memberId'] = str(data['char']['memberId'])
            data['marks'] = []
            for r in MarksTable().list(data['char']['memberId'], MarksTable().year()):
                data['marks'].append(r[5])
        s = json.dumps(data, indent=4, ensure_ascii=False)
        response = HttpResponse(s)
        response['Content-Type'] = 'application/json'
        return response
    names = {}
    for ch in CharacterTable().list():
        names[ch[4]] = ch[0]
    print(names)
    return JsonResponse(names, safe=False, json_dumps_params={'ensure_ascii': False})


def modify(request):
    def set(data, name, value):
        i = name.find('.')
        if name in data or i<0:
            data[name] = value
        else:
            dn = name[0:i]
            if dn not in data:
                data[dn] = {}
            set(data[dn], name[i+1:], value)
    print(request.POST.keys())
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
    return HttpResponse(request.method)


def pdf(request):
    if 'id' in request.GET:
        pc = Character.get_by_id(request.GET['id'])
        if pc:
            from pdf.sheet import Sheet
            sheet = Sheet(pc)
            import tempfile

            fp = next(tempfile._get_candidate_names())+"_tmp.pdf"
            sheet.output(fp, 'F')
            response = FileResponse(open(fp, 'rb'), filename=f"{pc.name}.pdf")
            response['Content-Type'] = 'application/pdf'
            return response
        else:
            return HttpResponse(f"Nem találom: '{request.GET['id']}")
    else:
        return HttpResponse(f"hiányzó paraméter: 'ch'")
