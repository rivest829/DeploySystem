# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
#业务逻辑代码

def login(request):
    error_msg = ''
    if request.method=='POST':
        user=request.POST.get('user',None)
        pwd=request.POST.get('pwd',None)
        if user == 'rivest829' and pwd == 'jiang123':
            return render(request, 'deploy.html')
        else:
            error_msg='用户名密码错误'
    # with open('templates/login.html','r') as f:
    #     html=f.read()
    # return HttpResponse(html)
    #相当于：
    return render(request, 'login.html', {'error_msg':error_msg})

def deploy(request):
    if request.method=='POST':
        if (request.POST.get('upload',None))=='部署':
            return render(request, 'upload.html')
    if request.method=='POST':
        if (request.POST.get('execute',None))=='重启服务':
            return render(request, 'execute.html')