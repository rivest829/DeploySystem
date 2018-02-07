# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from __future__ import unicode_literals
from pyecharts import Bar,Timeline
from django.template import loader
from pyecharts.constants import DEFAULT_HOST
from django.shortcuts import HttpResponse
import os,json,time,threading

def cpu():
    attr = ["172.16.1.165", "172.16.1.166","172.16.1.167","172.16.1.170","172.16.1.171"]
    v1 = build_visual_data('cpu')
    bar = Bar("CPU状态")
    bar.add("", attr, v1, is_label_show=True,mark_point=["max"],is_random=True,yaxis_formatter='‰')
    return bar

def mem():
    attr = ["172.16.1.165", "172.16.1.166", "172.16.1.167", "172.16.1.170", "172.16.1.171"]
    v1 = build_visual_data('mem')
    bar = Bar("内存状态")
    bar.add("", attr, v1, is_label_show=True,mark_point=["max"],is_random=True,yaxis_formatter='MB')
    return bar

def disk():
    attr = ["172.16.1.165", "172.16.1.166", "172.16.1.167", "172.16.1.170", "172.16.1.171"]
    v1 = build_visual_data('disk')
    bar = Bar("磁盘状态")
    bar.add("", attr, v1, is_label_show=True,mark_point=["max"],is_random=True,yaxis_formatter='GB')
    return bar


def build_visual_data(info_type):
    servername_list = ['bpdcap', 'cgdgw', 'csdacm', 'gsdpay', 'bsdbui']
    info = []
    for servername in servername_list:
        if info_type=='cpu':
            fab = 'fab --roles=%s define:value=%s doSysInfo -f fabfile.py' % (servername, 'uptime')
            out = os.popen(fab).read().decode('gb18030').encode('utf-8').split('[')[5].split()[13]
        elif info_type=='mem':
            fab = 'fab --roles=%s define:value=%s doSysInfo -f fabfile.py' % (servername, 'mem')
            out = os.popen(fab).read().decode('gb18030').encode('utf-8').split('[')[6].split()[4]
        elif info_type=='disk':
            fab = 'fab --roles=%s define:value=%s doSysInfo -f fabfile.py' % (servername, 'df')
            out = os.popen(fab).read().decode('gb18030').encode('utf-8').split('[')[6].split()[4].replace('G','')
            diskfile=open('diskout','ab')
            diskfile.write(out)
        info.append(out)
    return info

def visual_data_output(request):
    template = loader.get_template('deploy.html')
    with open('temp_json_info','rb') as temp_file:
        context_json=temp_file.read().decode()
        context=json.loads(context_json)
    return HttpResponse(template.render(context, request))

def flush_visual_data():
    while True:
        timeline = Timeline(is_auto_play=True, timeline_bottom=0)
        cpudata = cpu()
        memdata = mem()
        diskdata = disk()
        timeline.add(cpudata, 'CPU')
        timeline.add(memdata, '内存')
        timeline.add(diskdata, '磁盘')
        context = dict(
            visual_sysinfo=timeline.render_embed(),
            host=DEFAULT_HOST,
            script_list=timeline.get_js_dependencies(),
        )
        context_json = json.dumps(context)
        with open('temp_json_info','wb') as temp_file:
            temp_file.write(context_json)
        time.sleep(600)

def start_flush_visual_data():
    t=threading.Thread(target=flush_visual_data)
    t.setDaemon(True)
    t.start()