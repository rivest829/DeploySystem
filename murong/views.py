# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import os, time

# Create your views here.
# 业务逻辑代码


def login(request):
    error_msg = ''
    if request.method == 'POST':
        user = request.POST.get('user', None)
        pwd = request.POST.get('pwd', None)
        if user == 'rivest829' and pwd == 'jiang123':
            return render(request, 'deploy.html')
        else:
            error_msg = '用户名密码错误'
    # with open('templates/murong.html','r') as f:
    #     html=f.read()
    # return HttpResponse(html)
    # 相当于：
    return render(request, 'login.html', {'error_msg': error_msg})


def deploy(request):
    if request.method == 'POST':
        if (request.POST.get('upload', None)) == '部署':
            return render(request, 'upload.html')
    if request.method == 'POST':
        if (request.POST.get('execute', None)) == '重启服务':
            return render(request, 'execute.html')


def upload(request):
    pack = request.FILES.get('data')
    servername = request.POST.get('server')
    operator = request.POST.get('operator')
    save_path=os.path.join('pack',pack.name)
    package=open(save_path,mode="wb")
    for i in pack.chunks():
        package.write(i)
    package.close()
    uouter = os.popen('fab --roles=%s define:value=%s doWork' % (servername, pack.name)).read()
    with open("updLog/uploadLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt", 'a') as f:
        f.write(uouter + 'operator:' + operator)
    return render(request, 'result.html')
''' + uouter.replace('[', '<br>[') + '<br><br>执行人：' + operator + '''


def execute(request):
    servername = request.POST.get('server')
    operator = request.POST.get('operator')
    command = '\'ygstart ' + request.POST.get('GorS') + ' ' + request.POST.get('command') + ';yglist -a' + '\''
    eouter = os.popen('fab --roles=%s define:value=%s doExecute' % (servername, command)).read()
    # with open("exeLog/executeLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt", 'a') as f:
    #     f.write(eouter + 'operator:' + operator)

    return render(request, 'result.html')

''' + eouter.replace('[', '<br>[') + '<br><br>执行人：' + operator + '''