# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
#建表用ORM
#python manage.py migrate执行建表
#python manage.py createsuperuser创建超级用户
# Create your models here.
class UserInfo(models.Model):
    username=models.CharField(max_length=32)
    password=models.CharField(max_length=32)
    Permissions=models.TextField(max_length=322)