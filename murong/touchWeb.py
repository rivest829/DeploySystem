# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from django.shortcuts import render_to_response
import os,models,time
'''刷新WEB工程'''
def touchWeb(request):
    user = request.COOKIES.get('user', '')
    allow_server = models.UserInfo.objects.filter(username=user).get().Permissions.split(' ')
    password = request.POST.get('password')
    if password == 'touchtouch':
        servername = request.POST.get('server')
        target = request.POST.get('target')
        do_fab = 'fab --roles=%s define:value=%s definedate:log_date=%s doTouch -f fabfile.py' % (
            servername, servername, target)
        do_dellog = os.popen(do_fab)
        log_outer = do_dellog.read().decode('gb18030').encode('utf-8')
        result = log_outer.split('[')
        return render_to_response("resultDeploy.html",
                                  {'result': result, 'user': user, 'log_info': '成功', 'successTag': True})
    else:
        error_msg = '口令错！'
        return render_to_response('touch.html', {'error_msg': error_msg, 'permissions': allow_server})