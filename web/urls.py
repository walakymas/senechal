"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^favicon\.ico$',RedirectView.as_view(url='/static/images/favicon.ico')),
    path('', views.index, name='index'),
    path('json', views.get_character, name='json'),
    path('mark', views.mark, name='mark'),
    path('event', views.event, name='event'),
    path('pdf', views.pdf, name='pdf'),
    path('modify', views.modify, name='modify'),
    path('npc', views.npc, name='npc'),
    path('players', views.pcs, name='players'),
    path('newchar', views.newchar, name='newchar'),
    path('base', views.base, name='base'),
    path('list', views.list, name='list'),
]
