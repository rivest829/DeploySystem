#!/use/bin/env python
# encoding:utf-8
# author:Jiang Xinhan
# Example:
# fab --roles=cgdgw define:value='uat-cgdgw-20171020-865.zip' doWork
# fab --roles=cgdgw define:value='ps -aux' doExecute

from fabric.api import *
import zipfile

# Global Args
pack_dir = './pack/'

env.roledefs = {
    'username': ['username@ip', ],
}


def define(value):
    package = value
    command = value
    global package, command



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
def commander():
    run(command)


@roles()
def jboss():
    run('sh ~/jboss5/bin/start.sh')
    run('ygstart -a')

def doWork():
    execute(upload)
    execute(unzip)


def doExecute():
    execute(commander)

def doJboss():
    execute(jboss)
