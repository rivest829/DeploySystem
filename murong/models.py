# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
#建表用ORM
#python manage.py makemigrations
#python manage.py migrate执行建表
#python manage.py createsuperuser创建超级用户
# Create your models here.
import django.utils.timezone as timezone
class UserInfo(models.Model):
    username=models.CharField(max_length=32)
    password=models.CharField(max_length=32)
    Permissions=models.TextField(max_length=322)
class DeploySteps(models.Model):
    requestNum=models.CharField(max_length=32)#需求号
    developer=models.CharField(max_length=32)#开发者
    serverName = models.CharField(max_length=32,default="unknown")  # 模块名
    deployStep = models.TextField(max_length=322)#部署步骤
    extantionStep=models.TextField(max_length=322)#额外步骤
    deployTime=models.DateTimeField(default=timezone.now())