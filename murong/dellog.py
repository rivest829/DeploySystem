# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
import models,os,time
from django.shortcuts import render_to_response
'''
清理日志功能
'''
def dellog(request):
    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    if request.POST.has_key('Delete Log!'):
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
        else:
            error_msg = '口令错！'
            return render_to_response('dellog.html', {'error_msg': error_msg, 'permissions': allow_server})