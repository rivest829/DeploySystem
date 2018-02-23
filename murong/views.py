# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import os, time
from murong import models
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
        if (request.POST.get('administrator', None)) == '后台':
            return HttpResponseRedirect('/admin')
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
    if request.GET.get('back', ''):
        return visual_cpu(request)
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
    import bussiness_log_finder
    return bussiness_log_finder.greplog(request)


@csrf_exempt
def resultGreplog(request):
    import bussiness_log_finder
    return bussiness_log_finder.catlog(request)


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
    import dellog
    return dellog.dellog(request)


@csrf_exempt
def touch(request):
    import touchWeb
    return touchWeb.touchWeb(request)


@csrf_exempt
def sysInfo(request):
    import sysInfo
    return sysInfo.sysInfo(request)