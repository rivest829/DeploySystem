# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, render_to_response, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import os, time
from murong import models
import json
from django.template import loader
from pyecharts.constants import DEFAULT_HOST
# 重写
from datetime import datetime, timedelta, tzinfo
import build_visual_data

# TODO
# 1、__MACOSX问题
# 2、拖拽上传
class GMT8(tzinfo):
    delta = timedelta(hours=8)

    def utcoffset(self, dt):
        return self.delta

    def tzname(self, dt):
        return "GMT+8"

    def dst(self, dt):
        return self.delta


# 代码复用
def queryset_to_list(queryset):
    allCallbackData = []
    for stepObj in queryset:
        rowData = (stepObj.id, stepObj.developer, stepObj.requestNum, stepObj.deployStep, stepObj.extantionStep,
                   stepObj.serverName, str(stepObj.deployTime).split('.')[0])
        allCallbackData.append(rowData)
    return allCallbackData


# Create your views here.
# 业务逻辑代码

@csrf_exempt
def login(request):
    error_msg = ''
    user = request.POST.get('user', None)
    pwd = request.POST.get('pwd', None)
    if request.method == 'POST':
        if (request.POST.get('sysinfo', None)) == '查看系统状态':
            sysinfo = sysInfo('cgdgw')
            return render_to_response('login.html', {'sysinfo': sysinfo})
        if (request.POST.get('register', None)) == '注册':
            alert = '用户注册请联系运维人员'
            return render_to_response('login.html', {'alert': alert})
        if user == '':
            error_msg = '用户名为空'
        else:
            try:
                pwd_in_db = models.UserInfo.objects.filter(username=user).get().password
            except:
                error_msg = '用户不存在'
                return render(request, 'login.html', {'error_msg': error_msg})
            if pwd_in_db == pwd:

                response = visual_cpu(request)
                # 将username写入浏览器cookie
                response.set_cookie('user', user)
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
        if (request.POST.get('execute', None)) == '重启':
            return render_to_response('execute.html', {'permissions': allow_server})
        if (request.POST.get('dellog', None)) == 'dellog':
            return render_to_response('dellog.html', {'permissions': allow_server, 'date_list': date_list})
        if (request.POST.get('touch', None)) == 'touch':
            return render_to_response('touch.html', {'permissions': allow_server})
        if (request.POST.get('stepResponse', None)) == '部署记录':
            return render_to_response('stepResponse.html')
        if (request.POST.get('sysInfo', None)) == '系统状态':
            return render_to_response('sysInfo.html', {'permissions': allow_server})
        if (request.POST.get('exit', None)) == '注销':
            return HttpResponseRedirect('/murong/')
        if (request.POST.get('greplog', None)) == '业务日志':
            return render_to_response('greplog.html', {'permissions': allow_server, 'date_list': date_list})

@csrf_exempt
def visual_cpu(request):
    template = loader.get_template('deploy.html')
    cpu = build_visual_data.cpu()
    mem = build_visual_data.mem()
    context = dict(
        cpu_myechart=cpu.render_embed(),
        mem_myechart=mem.render_embed(),
        host=DEFAULT_HOST,
        script_list=cpu.get_js_dependencies()+mem.get_js_dependencies(),
    )
    return HttpResponse(template.render(context, request))

@csrf_exempt
def greplog(request):
    logfile_dict_list = []
    grepTarget = request.POST.get('grepTarget')
    servername = request.POST.get('server')
    log_date = request.POST.get('log_date')
    if servername == '' or log_date == '':
        return render_to_response("resultGreplog.html", {"grep_result": logfile_dict_list, 'error_msg': '填入信息不完整'})
    elif len(grepTarget) < 2:
        return render_to_response("resultGreplog.html", {"grep_result": logfile_dict_list, 'error_msg': '关键字长度不能小于2'})
    do_fab = 'fab --roles=%s define:value=%s definedate:log_date=%s defineGrepTarget:grepTarget=%s doGreplog -f fabfile.py' % (
        servername, servername, log_date, grepTarget)
    do_dellog = os.popen(do_fab.decode('utf-8').encode('gb18030'))
    greplog_row_string = do_dellog.read().decode('gb18030').encode('utf-8')
    greplog_list = greplog_row_string.split('out:')
    del greplog_list[0:1], greplog_list[-1]
    if len(greplog_list[0].split()) < 7:
        return render_to_response("resultGreplog.html", {"grep_result": logfile_dict_list, 'error_msg': '查无此关键字'})
    elif len(greplog_list) > 10000:
        return render_to_response("resultGreplog.html", {"grep_result": logfile_dict_list, 'error_msg': '大于一万条，放弃'})
    for row in greplog_list:
        logfile = row.split()
        dict_logfile = {logfile[7]: logfile[8], }
        logfile_dict_list.append(dict_logfile)
    response = render_to_response("resultGreplog.html", {"grep_result": logfile_dict_list})
    response.set_cookie('Log_servername', servername)
    response.set_cookie('log_date', log_date)
    return response


@csrf_exempt
def resultGreplog(request):
    cat_list = []
    logname = request.GET.get('logname')
    servername = request.COOKIES.get('Log_servername', '')
    log_date = request.COOKIES.get('log_date', '')
    do_fab = 'fab --roles=%s define:value=%s definedate:log_date=%s defineGrepTarget:grepTarget=%s doCatlog -f fabfile.py' % (
        servername, servername, log_date, logname)
    do_catlog = os.popen(do_fab)
    result_catlog = do_catlog.read().decode('gb18030').encode('utf-8')
    catlog_list = result_catlog.split('out:')
    del catlog_list[0], catlog_list[-1]
    for row in catlog_list:
        row_list = row.split('[')
        del row_list[-1]
        cat_list.append(row_list)
    return render_to_response("resultCatlog.html", {"grep_result": cat_list})


@csrf_exempt
def stepResponse(request):
    reqNum = request.POST.get('reqNum')
    developer = request.POST.get('developer')
    if len(reqNum) == 0:
        stepQueryset = models.DeploySteps.objects.filter(developer=developer).order_by("id")
    else:
        stepQueryset = models.DeploySteps.objects.filter(requestNum__contains=reqNum).order_by("id")
    global stepQueryset
    allCallbackData = queryset_to_list(stepQueryset)
    response = render_to_response('stepCallback.html', {'allres': allCallbackData})
    response.set_cookie('steps', json.dumps(allCallbackData), 3600)
    return response


@csrf_exempt
def stepCallback(request):
    if request.GET.get('back', ''):
        return render_to_response('deploy.html')
    if request.GET.get('duplicate', ''):
        allCallbackData = []
        duplicate_list = []
        stepQueryset_reverse = stepQueryset.reverse()
        for stepObj in stepQueryset_reverse:
            rowData = (stepObj.id, stepObj.developer, stepObj.requestNum, stepObj.deployStep, stepObj.extantionStep,
                       stepObj.serverName, str(stepObj.deployTime).split('.')[0])
            if rowData[3] in duplicate_list:
                continue
            duplicate_list.append(rowData[3])
            allCallbackData.append(rowData)
        response = render_to_response('stepCallback.html', {'allres': allCallbackData})
        response.set_cookie('steps', json.dumps(allCallbackData), 3600)
        return response
    if request.GET.get('order_type', ''):
        order_type = request.GET.get('order_type', '')
        orderset = stepQueryset.order_by(order_type)
        allCallbackData = queryset_to_list(orderset)
        response = render_to_response('stepCallback.html', {'allres': allCallbackData})
        response.set_cookie('steps', json.dumps(allCallbackData), 3600)
        return response
    if request.GET.get('stepout', ''):
        dict_stepout = {}
        allCallbackData = json.loads(request.COOKIES.get('steps', '').encode('utf-8'))
        if allCallbackData == '':
            allCallbackData = queryset_to_list(stepQueryset)
        stepout = ''
        for row in allCallbackData:
            if row[5] in dict_stepout:
                dict_stepout[row[5]] += ';' + row[3].replace('\'', '')
            else:
                dict_stepout[row[5]] = row[3].replace('\'', '')
        for key in dict_stepout:
            stepout += key + ':================' + dict_stepout[key] + '<br>'
        return HttpResponse(stepout)


@csrf_exempt
def upload(request):
    filnal_command = ''
    if request.GET.get('back', ''):
        return visual_cpu(request)
    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    pack = request.FILES.get('data')
    servername = pack.name.split('-')[1]
    save_path = os.path.join('pack', pack.name)
    if (')' in pack.name):
        error_msg = '文件名不可包含括号'
        return render(request, 'upload.html', {'error_msg': error_msg, 'permissions': allow_server})
    package = open(save_path, mode="wb")
    for item in pack.chunks():
        package.write(item)
    package.close()
    do_fab = 'fab --roles=%s define:value=%s doWork' % (servername, pack.name)
    do_upload = os.popen(do_fab)
    uouter = do_upload.read().decode('gb18030').encode('utf-8')
    result = uouter.split('[')
    if '/action/' in uouter:  # 如果能检测到包中有交易，自动重启服务
        file_list = []
        command_list = []
        uouter_list = uouter.split('out:')
        for i in uouter_list:
            if '/action/' in i:
                file_list.append(i)
        for i in file_list:
            command = i.split('/')[-2]
            if command not in command_list:
                command_list.append(command)
        for command in command_list:
            filnal_command += 'ygstart -s ' + command + ';'
        do_fab = 'fab --roles=%s define:value=%s doExecute -f fabfile.py' % (servername, '\'' + filnal_command + '\'')
        do_execute = os.popen(do_fab)
        eouter = do_execute.read().decode('gb18030').encode('utf-8')
        log_path = os.path.join('updLog', "exeUpdLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
        with open(log_path, mode='a') as f:
            f.write(uouter + eouter + '**************operator:' + user)
        eresult = result + eouter.split('[')
        bigAutoExe = '已自动重启服务' + filnal_command
        log_info = '本次执行日志已保存至' + log_path
        if 'succeed' in eresult[-2]:
            successTag = True
            models.DeploySteps.objects.create(
                requestNum='自动重启',
                developer=user,
                deployStep=command,
                extantionStep='自动重启',
                serverName=servername,
            )
        else:
            successTag = False
        return render_to_response("resultDeploy.html",
                                  {'result': eresult, 'user': user, 'log_info': log_info,
                                   'successTag': successTag, 'bigAutoExe': bigAutoExe})

    log_path = os.path.join('updLog', "uploadLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
    with open(log_path, mode='a') as f:
        f.write(uouter + "**************operator:" + user)
    log_info = '本次执行日志已保存至' + log_path
    if pack.name in result[-1]:
        successTag = True
    else:
        successTag = False
    return render_to_response("resultDeploy.html",
                              {'result': result, 'user': user, 'log_info': log_info, 'successTag': successTag})


@csrf_exempt
def execute(request):
    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    if request.POST.has_key('execute'):
        servername = request.POST.get('server')
        group_or_single = request.POST.get('GorS')
        requestNum = request.POST.get('requestNum', '')
        module_name = request.POST.get('command', '')
        extantionStep = request.POST.get('extantionStep')
        if requestNum == '':
            err = '请输入需求号！'
            return render_to_response('execute.html', {'permissions': allow_server, 'err': err})
        elif servername == 'unknown':
            err = '请选择部署目标！'
            return render_to_response('execute.html', {'permissions': allow_server, 'err': err})
        elif group_or_single == '':
            err = '请指定ygstart参数！'
            return render_to_response('execute.html', {'permissions': allow_server, 'err': err})
        elif module_name == '':
            err = '请输入服务名！'
            return render_to_response('execute.html', {'permissions': allow_server, 'err': err})
        command = '\'ygstart ' + group_or_single + ' ' + module_name + '\''
        do_fab = 'fab --roles=%s define:value=%s doExecute -f fabfile.py' % (servername, command)
        do_execute = os.popen(do_fab)
        eouter = do_execute.read().decode('gb18030').encode('utf-8')
        log_path = os.path.join('exeLog', "executeLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
        with open(log_path, mode='a') as f:
            f.write(eouter + '**************operator:' + user)
        result = eouter.split('[')
        log_info = '本次执行日志已保存至' + log_path
        if 'succeed' in result[-2]:
            successTag = True
            models.DeploySteps.objects.create(
                requestNum=requestNum,
                developer=user,
                deployStep=command,
                extantionStep=extantionStep,
                serverName=servername,
            )
        else:
            successTag = False
        return render_to_response("resultDeploy.html",
                                  {'result': result, 'user': user, 'log_info': log_info,
                                   'successTag': successTag})


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
            return render_to_response("resultDeploy.html",
                                      {'result': result, 'user': user, 'log_info': log_info, 'successTag': True})


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
            return render_to_response("resultDeploy.html",
                                      {'result': result, 'user': user, 'log_info': log_info, 'successTag': True})
        else:
            error_msg = '口令错！'
            return render(request, 'touch.html', {'error_msg': error_msg, 'permissions': allow_server})


@csrf_exempt
def sysInfo(request):
    dict_in_list = []
    servername = request.POST.get('server')
    info_type = request.POST.get('info_type')
    do_fab = 'fab --roles=%s define:value=%s doSysInfo -f fabfile.py' % (servername, info_type)
    fab_out = os.popen(do_fab).read().decode('gb18030').encode('utf-8')
    if info_type == 'uptime':
        uptime = fab_out.split('[')[5].split()
        html_type = "resultSysinfo.html"
        servername += '系统状态'
        dict_in_list = [{'服务器当前时间': uptime[2], },
                        {'服务器运行时间': uptime[4], },
                        {'当前用户数量': uptime[7], },
                        {'1分钟内系统平均负载': uptime[11], },
                        {'5分钟内系统平均负载': uptime[12], },
                        {'15分钟内系统平均负载': uptime[13], },
                        ]
    elif info_type == 'process':
        html_type = "resultProcess.html"
        process = fab_out.split('out:')  # 使用out:分割字符串形成行列表
        process = process[2:]  # 去除前两行无用消息
        for row in process:
            split_row = row.split()  # 行分割为列
            del split_row[-1]  # 删除最后一列，无用列
            if len(split_row) > 8:  # CMD中有空格因此会被分割，当CMD被分割时长度会大于预计的8
                cmd = ''
                for i in split_row[7:]:
                    cmd += i + ' '
                split_row[7] = cmd
                dict_in_list.append(split_row[0:8])
                continue
            dict_in_list.append(split_row)
        del dict_in_list[-1]
    return render_to_response(html_type, {'result': dict_in_list, 'servername': servername})
