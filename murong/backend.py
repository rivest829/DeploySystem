# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
from django.shortcuts import render,HttpResponse
import models
from random import sample

def show_user(request):
    user_dict={}
    user_queryset = models.UserInfo.objects.all()
    for user in user_queryset:
        user_dict[user.username]=user.password
    return render(request, 'backendadmin.html', {'user_dict': user_dict})
def return_user_permisson(request):
    username = request.GET.get('set_permission')
    global username
    userpermisson=models.UserInfo.objects.filter(username=username).get().Permissions
    return render(request,'set_user_permission.html',{'username':username,'permissions':userpermisson})
def set_user_permission(request):
    permisson=request.POST.get('permissions')
    user_queryset=models.UserInfo.objects.get(username=username)
    user_queryset.Permissions=permisson
    user_queryset.save()
    return HttpResponse('修改成功：<br>用户名：'+username+'<br>权限列表：'+permisson)

def del_user(request,username):
    user=models.UserInfo.objects.get(username=username)
    user.delete()
    return show_user(request)

def add_user(request):
    username = request.POST.get('username')
    password =randompassword()
    permissions = request.POST.get('permissons')
    user=models.UserInfo.objects.create(username=username,password=password,Permissions=permissions)
    user.save()
    return HttpResponse('添加用户成功！<br>用户名：'+username+'<br>密码：'+password+'<br>权限：'+permissions+'<br>返回到用户列表后请刷新')


def randompassword():
    password_list = ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g',
                     'f', 'e', 'd', 'c', 'b', 'a',
                     '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                     'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                     'U', 'V', 'W', 'X', 'Y', 'Z'
                     ]

    leng = 16  # 定义长度
    password = "".join(sample(password_list, leng)).replace(' ', '')
    return password