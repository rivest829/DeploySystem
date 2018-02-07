#!/use/bin/env python
# encoding:utf-8
# author:Jiang Xinhan
# Example:

from fabric.api import *
import zipfile,pickle,time,sys

# Global Args
pack_dir = './pack/'
serverInfo=open("serverInfo.cfg","rb")

env.roledefs = pickle.load(serverInfo)


def define(value):
    package = value
    command = value
    global package, command

def definedate(log_date):
    date = log_date
    global date

def defineGrepTarget(grepTarget):
    grep_target = grepTarget
    global grep_target

@roles()
def upload():
    put(pack_dir + package)


@roles()
def unzip():
    run('unzip -o ' + package + ' -d ../')
    flag = zipfile.ZipFile(pack_dir + package)
    for item in flag.namelist():
        tag = item.split('.')[0]
        if tag.endswith('-sit'):
            with cd('../'):
                run('mv ' + item + ' ' + item.replace('-sit', ''))
        elif tag.endswith('-uat'):
            with cd('../'):
                run('mv ' + item + ' ' + item.replace('-uat', ''))
        else:
            pass
    run('rm -f ' + package)

@roles()
def all_unzip():
        run('unzip -o ' + package)
        run('cp -r base/* .')
        run('rm -r base')

@roles()
def commander():
    run(command)

@roles()
def dellog():
    with cd('/home/%s/trc'%command):
        run('rm -rf %s'%date)

@roles()
def greplog():
    with cd('/home/%s/trc/%s'%(command,date)):
        run('grep -rl %s *|xargs ls -lrt'%grep_target)

@roles()
def catlog():
    with cd('/home/%s/trc/%s'%(command,date)):
        run('cat %s'%grep_target)

@roles()
def touch():
    with cd('/home/%s/jboss5/server/default/deploy/%s.war/WEB-INF'%(command,date)):
        run('touch web.xml')

@roles()
def jboss():
    run('sh ~/jboss5/bin/start.sh', pty=False)
    run('ygstart -a')

@roles()
def sysInfo():
    if package=='uptime':
        run('uptime')
    elif package=='process':
        run('ps -ef')
    elif package=='mem':
        run('free -m')
    elif package=='df':
        run('df -lh')
def doWork():
    execute(upload)
    execute(unzip)

def doBaseDeploy():
    execute(upload)
    execute(all_unzip)

def doCatlog():
    execute(catlog)

def doExecute():
    execute(commander)

def doJboss():
    execute(jboss)

def doDellog():
    execute(dellog)

def doGreplog():
    execute(greplog)

def doTouch():
    execute(touch)

def doSysInfo():
    execute(sysInfo)