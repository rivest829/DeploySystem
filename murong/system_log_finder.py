# -*- coding:utf-8 -*-
# Author Hsinhan Chiang
import json
from views import models
from django.shortcuts import render_to_response,HttpResponse

def queryset_to_list(queryset):
    allCallbackData = []
    for stepObj in queryset:
        rowData = (stepObj.id, stepObj.developer, stepObj.requestNum, stepObj.deployStep, stepObj.extantionStep,
                   stepObj.serverName, str(stepObj.deployTime).split('.')[0])
        allCallbackData.append(rowData)
    return allCallbackData

def system_log_finder(request):
    if request.POST.get('all_log')=='查询所有':
        stepQueryset = models.DeploySteps.objects.all().order_by('id')
    else:
        reqNum = request.POST.get('reqNum')
        developer = request.POST.get('developer')
        if len(reqNum) == 0:
            stepQueryset = models.DeploySteps.objects.filter(developer=developer).order_by("id")
        else:
            stepQueryset = models.DeploySteps.objects.filter(requestNum__contains=reqNum).order_by("id")
    global stepQueryset
    allCallbackData = queryset_to_list(stepQueryset.reverse())
    response = render_to_response('stepCallback.html', {'allres': allCallbackData})
    request.session['steps'] = json.dumps(allCallbackData)
    return response

def return_system_log_form(request):
    if request.GET.get('back', ''):
        return render_to_response('deploy.html')
    if request.GET.get('duplicate', ''):
        allCallbackData = []
        duplicate_list = []
        stepQueryset_reverse = stepQueryset.reverse()
        for stepObj in stepQueryset_reverse:
            rowData = (stepObj.id, stepObj.developer, stepObj.requestNum, stepObj.deployStep, stepObj.extantionStep,
                       stepObj.serverName, str(stepObj.deployTime).split('.')[0])
            if rowData[3] in duplicate_list:
                continue
            duplicate_list.append(rowData[3])
            allCallbackData.append(rowData)
        request.session['steps'] = json.dumps(allCallbackData)
        response = render_to_response('stepCallback.html', {'allres': allCallbackData})
        return response
    if request.GET.get('order_type', ''):
        order_type = request.GET.get('order_type', '')
        orderset = stepQueryset.order_by(order_type)
        allCallbackData = queryset_to_list(orderset)
        request.session['steps'] = json.dumps(allCallbackData)
        response = render_to_response('stepCallback.html', {'allres': allCallbackData})
        return response
    if request.GET.get('stepout', ''):
        dict_stepout = {}
        allCallbackData = json.loads(request.session.get('steps'))
        if allCallbackData == '':
            allCallbackData = queryset_to_list(stepQueryset)
        stepout = ''
        for row in allCallbackData:
            if row[5] in dict_stepout:
                dict_stepout[row[5]] += ';' + row[3].replace('\'', '')
            else:
                dict_stepout[row[5]] = row[3].replace('\'', '')
        for key in dict_stepout:
            stepout += key + ':================' + dict_stepout[key] + '<br>'
        return HttpResponse(stepout)