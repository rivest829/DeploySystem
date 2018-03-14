# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
import os,time
from views import models
from django.shortcuts import render_to_response
def execute(request):
    current_hour=int(time.strftime("%H", time.localtime()))
    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    if request.POST.has_key('execute'):
        servername = request.POST.get('server')
        group_or_single = request.POST.get('GorS')
        requestNum = request.POST.get('requestNum')
        module_name = request.POST.get('command', '')
        extantionStep = request.POST.get('extantionStep')
        if requestNum == '':
            err = '需求号获取失败，请输入需求号！'
            return render_to_response('execute.html',
                                      {'permissions': allow_server, 'err': err, 'requestNum': requestNum})
        elif servername == 'unknown':
            err = '请选择部署目标！'
            return render_to_response('execute.html',
                                      {'permissions': allow_server, 'err': err, 'requestNum': requestNum})
        elif group_or_single == '':
            err = '请指定ygstart参数！'
            return render_to_response('execute.html',
                                      {'permissions': allow_server, 'err': err, 'requestNum': requestNum})
        elif module_name == '':
            err = '请输入服务名！'
            return render_to_response('execute.html',
                                      {'permissions': allow_server, 'err': err, 'requestNum': requestNum})
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
                deployStep=command.replace('\'',''),
                extantionStep=extantionStep,
                serverName=servername,
            )
        else:
            successTag = False
        if current_hour<7:
            log_info='现在是%s点，go home and have a rest'
        return render_to_response("resultDeploy.html",
                                  {'result': result, 'user': user, 'log_info': log_info,
                                   'successTag': successTag})