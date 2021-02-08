from django.http import HttpResponse, JsonResponse
from django.http import HttpRequest


def index(request):
    return HttpResponse("Hello, world. You're at the senechal index.")

def yaml(request):
    if 'ch' in request.GET:
        from config import Config
        Config.reload()
        if request.GET['ch'] in Config.characters:
            return JsonResponse(Config.characters[request.GET['ch']], safe=False, json_dumps_params={'ensure_ascii': False})
        else:
            return HttpResponse(f"Nem találom: '{request.GET['ch']}' <br/>{Config.characters.keys()}")
    else:
        return HttpResponse(f"hiányzó paraméter: 'ch'")
