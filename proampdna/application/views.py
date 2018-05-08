# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render


# Create your views here.
def index_view(request):
    return render(request, 'application/index.html', {})


def application_view(request):
    return render(request, 'application/application.html', {})