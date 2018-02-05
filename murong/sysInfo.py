# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from django.shortcuts import render_to_response
import os
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
