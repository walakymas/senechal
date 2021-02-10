import json

from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.cache import never_cache

from character import Character
from database.charactertable import CharacterTable


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
        data = pc.get_data(False)
        if 'memberId' in data:
            data['memberId'] = str(data['memberId'])
        s = json.dumps(data, indent=4, ensure_ascii=False)
        response = HttpResponse(s)
        response['Content-Type'] = 'application/json'
        return response
    names = {}
    for ch in CharacterTable().list():
        names[ch[0]] = ch[4]
    print(names)
    return JsonResponse(names, safe=False, json_dumps_params={'ensure_ascii': False})


def modify(request):
    print(request.POST.keys())
    CharacterTable().set_json(request.POST['id'], request.POST['json'])
    return HttpResponse(request.method)


def pdf(request):
    if 'ch' in request.GET:
        from config import Config
        pc = Config.get_character(request.GET['ch'])
        if pc:
            from pdf.sheet import Sheet
            pdf = Sheet(pc)
            import tempfile
            fp = next(tempfile._get_candidate_names())
            pdf.output(fp, 'F')
            response = FileResponse(open(fp, 'rb'), filename=f"{pc['name']}.pdf")
            response['Content-Type'] = 'application/pdf'
            return response
        else:
            return HttpResponse(f"Nem találom: '{request.GET['ch']}' <br/>{Config.characters.keys()}")
    else:
        return HttpResponse(f"hiányzó paraméter: 'ch'")
