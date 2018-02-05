# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, render_to_response, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import os, time
from murong import models

# 重写
from datetime import timedelta, tzinfo


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
    requestNum = request.COOKIES.get('requestNum', '')
    servername = request.COOKIES.get('servername', '')
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
            return render_to_response('execute.html',
                                      {'permissions': allow_server, 'requestNum': requestNum, 'servername': servername})
        if (request.POST.get('dellog', None)) == 'dellog':
            return render_to_response('dellog.html', {'permissions': allow_server, 'date_list': date_list})
        if (request.POST.get('touch', None)) == 'touch':
            return render_to_response('touch.html', {'permissions': allow_server})
        if (request.POST.get('stepResponse', None)) == '部署记录':
            return render_to_response('stepResponse.html',{'user':user,'requestNum':requestNum})
        if (request.POST.get('sysInfo', None)) == '系统状态':
            return render_to_response('sysInfo.html', {'permissions': allow_server})
        if (request.POST.get('exit', None)) == '注销':
            return HttpResponseRedirect('/murong/')
        if (request.POST.get('greplog', None)) == '业务日志':
            return render_to_response('greplog.html', {'permissions': allow_server, 'date_list': date_list})


@csrf_exempt
def visual_cpu(request):
    import build_visual_data
    return build_visual_data.visual_data_output(request)


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
    return render_to_response("resultCatlog.html",
                              {"grep_result": cat_list, "log_name": servername + ' : ' + log_date + '日 : ' + logname})


@csrf_exempt
def stepResponse(request):
    import system_log_finder
    return system_log_finder.system_log_finder(request)


@csrf_exempt
def stepCallback(request):
    import system_log_finder
    return system_log_finder.return_system_log_form(request)


@csrf_exempt
def upload(request):
    import upload
    if request.GET.get('autorestart', ''):
        user = request.COOKIES.get('user', '')
        requestNum = request.COOKIES.get('requestNum', '')
        servername = request.COOKIES.get('servername', '')
        filnal_command = request.COOKIES.get('filnal_command', '')
        return upload.autorestart(requestNum, servername, filnal_command, user)
    return upload.upload(request)


@csrf_exempt
def execute(request):
    import execute
    return execute.execute(request)


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
