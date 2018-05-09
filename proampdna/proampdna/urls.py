"""proampdna URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from application.views import *
from django.contrib.staticfiles.views import serve
from django.views.generic import RedirectView

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', index_view),
    url(r'^application/$', serve, kwargs={'path': 'index.html'}),
    url(r'^api/load-species-data/$', SpecieViewSet.as_view({'get': 'load_species_data'})),
    url(r'^api/run-app/$', SpecieViewSet.as_view({'get': 'run_app'})),
    url(r'^(?!/?static/)(?!/?media/)(?P<path>.*\..*)$', RedirectView.as_view(url='/static/%(path)s', permanent=False)),
]
