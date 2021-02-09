from django.http import HttpResponse, JsonResponse, FileResponse


def index(request):
    return HttpResponse("Hello, world. You're at the senechal index.")


def json(request):
    if 'ch' in request.GET:
        from config import Config
        pc = Config.get_character(request.GET['ch'])
        if pc:
            return JsonResponse(pc, safe=False, json_dumps_params={'ensure_ascii': False})
        else:
            return HttpResponse(f"Nem találom: '{request.GET['ch']}' <br/>{Config.characters.keys()}")
    else:
        return HttpResponse(f"hiányzó paraméter: 'ch'")


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
