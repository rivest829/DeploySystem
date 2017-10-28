# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
#业务逻辑代码

def login(request):
    # with open('templates/login.html','r') as f:
    #     html=f.read()
    # return HttpResponse(html)
    #相当于：
    return render(request,'login.html')