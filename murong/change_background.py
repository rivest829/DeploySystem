# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from deploy import settings
import time,threading,random
def change_background():
    while True:
        i=random.randrange(1,12)
        read_pic=open('%s/%s.jpg'%(settings.STATIC_ROOT,i),'rb')
        write_pic=open('%s/bigbang.jpg'%settings.STATIC_ROOT,'wb')
        pic = read_pic.read()
        write_pic.write(pic)
        time.sleep(72000)
def start_change():
    change=threading.Thread(target=change_background)
    change.setDaemon(True)
    change.start()