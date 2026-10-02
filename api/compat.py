"""Minimal stand-ins for the few django.http pieces that views use.

They let ``api/views.py`` stay a line-for-line port of ``web/views.py`` while running
on aiohttp. A view is a plain synchronous function ``view(request) -> Response``;
``api/app.py`` runs it in a worker thread and converts the result to an aiohttp response.
"""
import datetime
import decimal
import functools
import json
import uuid

NO_CACHE = 'max-age=0, no-cache, no-store, must-revalidate, private'


class JSONEncoder(json.JSONEncoder):
    """Same output as django.core.serializers.json.DjangoJSONEncoder (the JsonResponse default)."""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            return r[:-6] + 'Z' if r.endswith('+00:00') else r
        if isinstance(o, (datetime.date, datetime.time)):
            r = o.isoformat()
            if isinstance(o, datetime.time) and o.microsecond:
                r = r[:12]
            return r
        if isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)
        return super().default(o)


class Request:
    def __init__(self, GET=None, POST=None):
        self.GET = GET or {}
        self.POST = POST or {}


class HttpResponse:
    def __init__(self, content='', content_type='text/html; charset=utf-8', status=200):
        self.content = content
        self.status = status
        self.headers = {'Content-Type': content_type}

    def __setitem__(self, name, value):
        self.headers[name] = value


class JsonResponse(HttpResponse):
    def __init__(self, data, safe=True, json_dumps_params=None, status=200):
        if safe and not isinstance(data, dict):
            raise TypeError('In order to allow non-dict objects to be serialized set safe=False')
        super().__init__(json.dumps(data, cls=JSONEncoder, **(json_dumps_params or {})),
                         'application/json', status)


class FileResponse(HttpResponse):
    def __init__(self, fileobj, filename=None, status=200):
        super().__init__(fileobj, 'application/octet-stream', status)
        if filename:
            self['Content-Disposition'] = f'inline; filename="{filename}"'


def never_cache(view):
    @functools.wraps(view)
    def wrapper(request):
        response = view(request)
        response['Cache-Control'] = NO_CACHE
        return response
    return wrapper
