# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse
import os, time
from murong import models

# Create your views here.
# 业务逻辑代码


def login(request):
    error_msg = ''
    if request.method == 'POST':
        user = request.POST.get('user', None)
        pwd = request.POST.get('pwd', None)
        if models.UserInfo.objects.get(username=user).password==pwd:
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
    save_path = os.path.join('pack', pack.name)
    package = open(save_path, mode="wb")
    for item in pack.chunks():
        package.write(item)
    package.close()
    do_fab ='fab --roles=%s define:value=%s doWork' % (servername, pack.name)
    do_upload=os.popen(do_fab)
    uouter =do_upload.read()
    log_path = os.path.join('updLog', "uploadLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
    with open(log_path, mode='a') as f:
        f.write(uouter + 'operator:' + operator)
    return HttpResponse('''<!DOCTYPE html>
<html lang="en">
<head>
    Murong Execute
</head>
<body>
<form>
    '''
                        + uouter.replace('[', '<br>[') + '<br><br>执行人：' + operator +
                        '''
                        </form>
                        </body>
                        </html>
                        </html>''')


def execute(request):
    servername = request.POST.get('server')
    operator = request.POST.get('operator')
    command = '\'ygstart ' + request.POST.get('GorS') + ' ' + request.POST.get('command')  + '\''
    do_fab='fab --roles=%s define:value=%s doExecute -f fabfile.py' % (servername, command)
    do_execute = os.popen(do_fab)
    eouter=do_execute.read()
    log_path = os.path.join('exeLog', "executeLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
    with open(log_path, mode='a') as f:
        f.write(eouter + '**************operator:' + operator)
    return HttpResponse('''<!DOCTYPE html>
<html lang="en">
<head>
    Murong Execute
</head>
<body>
<form>
    '''
                        + eouter.replace('[', '<br>[') + '<br><br>执行人：' + operator +
                        '''
                        </form>
                        </body>
                        </html>
                        </html>''')


