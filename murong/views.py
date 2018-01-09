# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, render_to_response,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os, time
from murong import models
import json
#代码复用
def queryset_to_list(queryset):
    allCallbackData=[]
    for stepObj in queryset:
        rowData = (stepObj.id, stepObj.developer, stepObj.requestNum, stepObj.deployStep, stepObj.extantionStep,
                   stepObj.serverName)
        allCallbackData.append(rowData)
    return allCallbackData
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
    user = request.COOKIES.get('user', '')
    date_list = []
    date_iter = (i for i in range(1, 32))
    for i in date_iter:
        if i < 10:
            date_list.append('0' + str(i))
        else:
            date_list.append(i)
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    if request.method == 'POST':
        if (request.POST.get('upload', None)) == '部署':
            return render_to_response('upload.html', {'permissions': allow_server})
        if (request.POST.get('execute', None)) == '重启服务':
            return render_to_response('execute.html', {'permissions': allow_server})
        if (request.POST.get('dellog', None)) == 'dellog':
            return render_to_response('dellog.html', {'permissions': allow_server, 'date_list': date_list})
        if (request.POST.get('touch', None)) == 'touch':
            return render_to_response('touch.html', {'permissions': allow_server})
        if (request.POST.get('stepResponse', None)) == '查询部署步骤':
            return render_to_response('stepResponse.html')


@csrf_exempt
def stepResponse(request):
    reqNum = request.POST.get('reqNum')
    developer = request.POST.get('developer')
    if len(reqNum) == 0:
        stepQueryset = models.DeploySteps.objects.filter(developer=developer).order_by("requestNum")
    else:
        stepQueryset = models.DeploySteps.objects.filter(requestNum=reqNum).order_by("requestNum")
    global stepQueryset
    allCallbackData=queryset_to_list(stepQueryset)
    response = render_to_response('stepCallback.html', {'allres': allCallbackData})
    response.set_cookie('steps', json.dumps(allCallbackData), 3600)
    return response


@csrf_exempt
def upload(request):
    if request.GET.get('duplicate',''):
        allCallbackData = []
        duplicate_list=[]
        for stepObj in stepQueryset:
            rowData = (stepObj.id, stepObj.developer, stepObj.requestNum, stepObj.deployStep, stepObj.extantionStep,
                       stepObj.serverName)
            if rowData[3] in duplicate_list:
                continue
            duplicate_list.append(rowData[3])
            allCallbackData.append(rowData)
        response=render_to_response('stepCallback.html', {'allres': allCallbackData})
        response.set_cookie('steps', json.dumps(allCallbackData), 3600)
        return response
    if request.GET.get('order_type', ''):
        order_type=request.GET.get('order_type', '')
        orderset=stepQueryset.order_by(order_type)
        allCallbackData=queryset_to_list(orderset)
        response = render_to_response('stepCallback.html', {'allres': allCallbackData})
        response.set_cookie('steps', json.dumps(allCallbackData), 3600)
        return response

    if request.GET.get('stepout', ''):
        allCallbackData= json.loads(request.COOKIES.get('steps', '').encode('utf-8'))
        if allCallbackData=='':
            allCallbackData=queryset_to_list(stepQueryset)
        stepout = ''
        for row in allCallbackData:
            stepout += row[3] + ';'
        return HttpResponse(stepout.replace('\'',''))


    if request.GET.get('back', ''):
        return render_to_response('deploy.html')


    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    error_msg = '服务器与包名不匹配'
    pack = request.FILES.get('data')
    servername = request.POST.get('server')
    save_path = os.path.join('pack', pack.name)
    if servername != pack.name.split('-')[1]:  # 校验包名与服务器名是否匹配
        return render(request, 'upload.html', {'error_msg': error_msg, 'permissions': allow_server})
    elif (')' in pack.name):
        error_msg = '文件名不可包含括号'
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
    result = uouter.split('[')
    log_info = '本次执行日志已保存至' + log_path
    if pack.name in result[-1]:
        successTag=True
    else:
        successTag=False
    return render_to_response("resultDeploy.html", {'result': result, 'user': user, 'log_info': log_info,'successTag':successTag})


@csrf_exempt
def execute(request):
    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    if request.POST.has_key('execute'):
        servername = request.POST.get('server')
        requestNum = request.POST.get('requestNum','')
        extantionStep = request.POST.get('extantionStep')
        if requestNum=='':
            err='请输入需求号'
            return render_to_response('execute.html', {'permissions': allow_server,'err':err})
        command = '\'ygstart ' + request.POST.get('GorS') + ' ' + request.POST.get('command') + '\''
        do_fab = 'fab --roles=%s define:value=%s doExecute -f fabfile.py' % (servername, command)
        do_execute = os.popen(do_fab)
        models.DeploySteps.objects.create(
            requestNum=requestNum,
            developer=user,
            deployStep=command,
            extantionStep=extantionStep,
            serverName=servername
        )
        eouter = do_execute.read().decode('gb18030').encode('utf-8')
        log_path = os.path.join('exeLog', "executeLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
        with open(log_path, mode='a') as f:
            f.write(eouter + '**************operator:' + user)
        result = eouter.split('[')
        log_info = '本次执行日志已保存至' + log_path
        if 'succeed' in result[-2]:
            successTag = True
        else:
            successTag = False
        return render_to_response("resultDeploy.html", {'result': result, 'user': user, 'log_info': log_info,'successTag':successTag})

@csrf_exempt
def dellog(request):
    user = request.COOKIES.get('user', '')
    if request.POST.has_key('Delete Log!'):
        allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
        password = request.POST.get('password')
        if password == 'dellog':
            servername = request.POST.get('server')
            log_date = request.POST.get('log_date')
            do_fab = 'fab --roles=%s define:value=%s definedate:log_date=%s doDellog -f fabfile.py' % (
                servername, servername, log_date)
            do_dellog = os.popen(do_fab)
            log_outer = do_dellog.read().decode('gb18030').encode('utf-8')
            log_path = os.path.join('exeLog', "deleteLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
            with open(log_path, mode='a') as f:
                f.write(log_outer + '**************operator:' + user)
            result = log_outer.split('[')
            log_info = '本次执行日志已保存至' + log_path
            return render_to_response("resultDeploy.html", {'result': result, 'user': user, 'log_info': log_info,'successTag':True})


@csrf_exempt
def touch(request):
    user = request.COOKIES.get('user', '')
    if request.POST.has_key('touch'):
        allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
        password = request.POST.get('password')
        if password == 'touchtouch':
            servername = request.POST.get('server')
            target = request.POST.get('target')
            do_fab = 'fab --roles=%s define:value=%s definedate:log_date=%s doTouch -f fabfile.py' % (
                servername, servername, target)
            do_dellog = os.popen(do_fab)
            log_outer = do_dellog.read().decode('gb18030').encode('utf-8')
            log_path = os.path.join('exeLog', "touchLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
            with open(log_path, mode='a') as f:
                f.write(log_outer + '**************operator:' + user)
            result = log_outer.split('[')
            log_info = '本次执行日志已保存至' + log_path
            return render_to_response("resultDeploy.html", {'result': result, 'user': user, 'log_info': log_info,'successTag':True})
        else:
            error_msg = '口令错！'
            return render(request, 'touch.html', {'error_msg': error_msg, 'permissions': allow_server})
