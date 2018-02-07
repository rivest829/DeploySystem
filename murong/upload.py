# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from views import visual_cpu, models
from django.shortcuts import render, render_to_response
import os, time


def upload(request):
    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    pack = request.FILES.get('data')
    split_pack_name = pack.name.split('-')
    servername = split_pack_name[1]
    if servername not in allow_server:
        error_msg = '你没有'+servername+'的权限'
        return render(request, 'upload.html', {'error_msg': error_msg})
    elif (')' in pack.name):
        error_msg = '文件名不可包含括号'
        return render(request, 'upload.html', {'error_msg': error_msg})
    requestNum = split_pack_name[2] + '-' + split_pack_name[3]
    save_path = os.path.join('pack', pack.name)
    package = open(save_path, mode="wb")
    for item in pack.chunks():
        package.write(item)
    package.close()
    do_fab = 'fab --roles=%s define:value=%s doWork' % (servername, pack.name)
    do_upload = os.popen(do_fab)
    uouter = do_upload.read().decode('gb18030').encode('utf-8')
    result = uouter.split('[')
    log_path = os.path.join('updLog', "uploadLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
    with open(log_path, mode='a') as f:
        f.write(uouter + "**************operator:" + user)
    log_info = '本次执行日志已保存至' + log_path
    if pack.name in result[-1]:
        successTag = True
    else:
        successTag = False
    if '/action/' in uouter:  # 如果能检测到包中有交易，自动重启服务
        filnal_command = ''
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
        response = render_to_response("resultDeploy.html",
                                      {'result': result, 'user': user, 'log_info': log_info, 'successTag': successTag,
                                       'filnal_command': filnal_command})
        response.set_cookie('filnal_command', filnal_command)
        response.set_cookie('requestNum', requestNum)
        response.set_cookie('servername', servername)
        return response
    response = render_to_response("resultDeploy.html",
                                  {'result': result, 'user': user, 'log_info': log_info, 'successTag': successTag,
                                   })
    response.set_cookie('requestNum', requestNum)
    response.set_cookie('servername', servername)
    return response


def autorestart(requestNum, servername, filnal_command, user):
    do_fab = 'fab --roles=%s define:value=%s doExecute -f fabfile.py' % (servername, '\'' + filnal_command + '\'')
    do_execute = os.popen(do_fab)
    eouter = do_execute.read().decode('gb18030').encode('utf-8')
    log_path = os.path.join('exeLog', "executeLog-" + time.strftime("%Y%m%d-%H%M", time.localtime()) + ".txt")
    with open(log_path, mode='a') as f:
        f.write(eouter + '**************operator:' + user)
    eresult = eouter.split('[')
    bigAutoExe = '已重启服务' + filnal_command
    log_info = '本次执行日志已保存至' + log_path
    if 'succeed' in eresult[-2]:
        successTag = True
        models.DeploySteps.objects.create(
            requestNum=requestNum,
            developer=user,
            deployStep=filnal_command,
            extantionStep='自动重启',
            serverName=servername,
        )
    else:
        successTag = False
    response = render_to_response("resultDeploy.html",
                                  {'result': eresult, 'user': user, 'log_info': log_info,
                                   'successTag': successTag, 'bigAutoExe': bigAutoExe})
    response.set_cookie('requestNum', requestNum)
    response.set_cookie('servername', servername)
    return response
