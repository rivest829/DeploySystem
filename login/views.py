# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse

# Create your views here.

def login(request):
    return HttpResponse('''
     <html>
            <head>
		Murong
            </head>
            <body>
                <form action"/login" method="post">
                    username:<input name="username" type="text" /><br>
                    password:<input name="password" type="password" /><br>
                    <input type="submit" value="Login" /><br>
                </form>
            </body>
        </html>'''
        )