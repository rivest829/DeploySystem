# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse,render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import os, time
from murong import models


# Create your views here.
# 业务逻辑代码

@csrf_exempt
def login(request):
    error_msg = ''
    pwd = 'fNv2MmUkSF05TAa4xhmVF26rJk3obniEIoKAUEZ5nMNGkmqy8'
    user = request.POST.get('user', None)
    pwd = request.POST.get('pwd', None)
    if request.method == 'POST':
        if user == '':
            error_msg = '用户名为空'
        else:
            try:
                pwd_in_db = models.UserInfo.objects.filter(username=user).get().password
            except:
                error_msg = '用户不存在'
                return render(request, 'login.html', {'error_msg': error_msg})
            if pwd_in_db == pwd:
                response = render_to_response('deploy.html')

                # 将username写入浏览器cookie,失效时间为3600
                response.set_cookie('user', user, 3600)
                return response
            else:
                error_msg = '用户名密码错误'
    return render(request, 'login.html', {'error_msg': error_msg})

@csrf_exempt
def deploy(request):
    user=request.COOKIES.get('user','')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    if request.method == 'POST':
        if (request.POST.get('upload', None)) == '部署':
            return render_to_response('upload.html', {'permissions': allow_server})
    if request.method == 'POST':
        if (request.POST.get('execute', None)) == '重启服务':
            return render_to_response('execute.html', {'permissions': allow_server})

@csrf_exempt
def upload(request):
    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    error_msg = '服务器与包名不匹配'
    pack = request.FILES.get('data')
    servername = request.POST.get('server')
    save_path = os.path.join('pack', pack.name)
    if servername != pack.name.split('-')[1]:
        return render(request, 'upload.html', {'error_msg': error_msg, 'permissions': allow_server})
    package = open(save_path, mode="wb")
    for item in pack.chunks():
        package.write(item)
    package.close()
    do_fab = 'fab --roles=%s define:value=%s doWork' % (servername, pack.name)
    do_upload = os.popen(do_fab)
    uouter = do_upload.read().decode('gb18030').encode('utf-8')
    log_path = os.path.join('updLog', "uploadLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
    with open(log_path, mode='a') as f:
        f.write(uouter + "**************operator:" + user)
    return HttpResponse('''<!DOCTYPE html>
<html lang="en">
<head>
    Murong Execute
</head>
<body>
<form>
    '''
                        + uouter.replace('[', '<br>[') + '<br><br>执行人：' + user +
                        '''
                        </form>
                        </body>
                        </html>
                        </html>''')

@csrf_exempt
def execute(request):
    user = request.COOKIES.get('user', '')
    if request.POST.has_key('execute'):
        servername = request.POST.get('server')
        command = '\'ygstart ' + request.POST.get('GorS') + ' ' + request.POST.get('command') + '\''
        do_fab = 'fab --roles=%s define:value=%s doExecute -f fabfile.py' % (servername, command)
        do_execute = os.popen(do_fab)
        eouter = do_execute.read().decode('gb18030').encode('utf-8')
        log_path = os.path.join('exeLog', "executeLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
        with open(log_path, mode='a') as f:
            f.write(eouter + '**************operator:' + user)
        return HttpResponse('''<!DOCTYPE html>
    <html lang="en">
    <head>
        Murong Execute
    </head>
    <body>
    <form>
        '''
                            + eouter.replace('[', '<br>[') + '<br><br>执行人：' +user+
                            '''
                            </form>
                            </body>
                            </html>
                            </html>''')

    elif request.POST.has_key('restartJboss'):
        servername=request.POST.get('server')
        do_fab = 'fab --roles=%s doJboss -f fabfile.py' % (servername)
        do_jboss = os.popen(do_fab)
        jouter = do_jboss.read().decode('gb18030').encode('utf-8')
        log_path = os.path.join('exeLog', "executeLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
        with open(log_path, mode='a') as f:
            f.write(jouter + '**************operator:' + user)
        return HttpResponse('''<!DOCTYPE html>
    <html lang="en">
    <head>
        Murong
    </head>
    <body>
    <form>
        '''
                            + jouter.replace('[', '<br>[') + '<br><br>执行人：' +user+
                            '''
                            </form>
                            </body>
                            </html>
                            </html>''')