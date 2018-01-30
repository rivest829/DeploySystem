# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from __future__ import unicode_literals
from pyecharts import Bar,Page
import os
servername_list=['bpdcap','cgdgw','csdacm','gsdpay','bsdbui']
cpu_info=[]
for servername in servername_list:
    do_fab = 'fab --roles=%s define:value=%s doSysInfo -f fabfile.py' % (servername, 'uptime')
    cpu_out=os.popen(do_fab).read().decode('gb18030').encode('utf-8').split('[')[5].split()[13]
    cpu_info.append(cpu_out)

def cpu():
    attr = ["172.16.1.165", "172.16.1.166","172.16.1.167","172.16.1.170","172.16.1.171"]
    v1 = cpu_info
    bar = Bar("CPU状态", width=720, height=360)
    bar.add("各服务器CPU状态", attr, v1, is_label_show=True)
    return bar

def mem():
    attr = ["内存使用", "内存空余"]
    v1 = [11, 12]
    pie = Bar("内存信息",width=720, height=360)
    pie.add("", attr, v1, is_label_show=True)
    return pie