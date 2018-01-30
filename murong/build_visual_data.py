# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from __future__ import unicode_literals
from pyecharts import Bar,Page
import os
servername_list=['bpdcap','cgdgw','csdacm','gsdpay','bsdbui']
cpu_info=[]
mem_info=[]
for servername in servername_list:
    cpu_fab = 'fab --roles=%s define:value=%s doSysInfo -f fabfile.py' % (servername, 'uptime')
    mem_fab = 'fab --roles=%s define:value=%s doSysInfo -f fabfile.py' % (servername, 'mem')
    cpu_out=os.popen(cpu_fab).read().decode('gb18030').encode('utf-8').split('[')[5].split()[13]
    mem_out=os.popen(mem_fab).read().decode('gb18030').encode('utf-8').split('[')[6].split()[4]
    cpu_info.append(cpu_out)
    mem_info.append(mem_out)

def cpu():
    attr = ["172.16.1.165", "172.16.1.166","172.16.1.167","172.16.1.170","172.16.1.171"]
    v1 = cpu_info
    bar = Bar("CPU状态", width=720, height=360)
    bar.add("各服务器CPU状态", attr, v1, is_label_show=True,mark_point=["max"],is_random=True)
    return bar

def mem():
    attr = ["172.16.1.165", "172.16.1.166", "172.16.1.167", "172.16.1.170", "172.16.1.171"]
    v1 = mem_info
    bar = Bar("内存状态", width=720, height=360)
    bar.add("各服务器CPU状态", attr, v1, is_label_show=True,mark_point=["max"],is_random=True)
    print(mem_info)
    return bar
