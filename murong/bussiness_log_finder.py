# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from django.shortcuts import render_to_response
import os
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
        try:
            dict_logfile = {logfile[7]: logfile[8], }
        except IndexError as e:
            return render_to_response("resultGreplog.html", {"grep_result": logfile_dict_list, 'error_msg': str(e)+'，可能是该日日志已被清空'})
        logfile_dict_list.append(dict_logfile)
    response = render_to_response("resultGreplog.html", {"grep_result": logfile_dict_list})
    response.set_cookie('Log_servername', servername)
    response.set_cookie('log_date', log_date)
    return response

def catlog(request):
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