import datetime
import difflib
import string
import urllib
from itertools import islice

import requests
import xlrd
import re

from django.core import mail
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.contrib import messages
from _mysql_exceptions import DataError, IntegrityError
from django.template import RequestContext

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import EmailMultiAlternatives

from django.core.files.storage import FileSystemStorage
import json
from django.contrib import auth
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.cache import cache_control

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import empty
from rest_framework.permissions import AllowAny
from xlrd import XLRDError
from time import gmtime, strftime
import time
from openpyxl.styles import PatternFill
import urllib.parse
import urllib.request
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import login, authenticate
from django.conf import settings
from django import forms
import sys

# Create your views here.
from vacay.models import Employee, InfoBuffer, CommonUser, MailBox, EatDrink, Job, Announce, Media, Watercooler, \
    Comment, Service, ProviderSchedule, Product, Contactor, Provider, AdminUser, RetailProduct, RetailDetail, Friend, \
    ContFriend


def welcome(request):
    email = ''
    try:
        if request.session['fb_email'] != '':
            email = request.session['fb_email']
            users = Friend.objects.filter(email=email)
            if users.count() > 0:
                request.session['em_company'] = ''
                return render(request, 'vacay/home_common.html', {'me_email': email})
            else:
                return redirect('/logout')
        else:
            return redirect('/logout')
    except KeyError:
        return redirect('/logout')

def logout(request):
    request.session['em_email'] = ''
    request.session['user'] = ''
    request.session['em_company'] = ''
    request.session['em_adminID'] = ''
    request.session['pro_email'] = ''
    request.session['pro_id'] = ''
    request.session['manager_email'] = ''
    request.session['manager_id'] = ''
    request.session['fb_first_name'] = ''
    request.session['fb_last_name'] = ''
    request.session['fb_photo'] = ''
    request.session['fb_gender'] = ''
    request.session['fb_email'] = ''
    request.session['ln_job'] = ''
    return render(request, 'vacay/welcome.html')

def employee_login_page(request):
    request.session['user'] = 'employee'      ########################################
    return render(request, 'vacay/user_login.html')

def provider_login_page(request):
    request.session['user'] = 'provider'      ########################################
    return render(request, 'vacay/user_login.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def login_user(request):
    if request.method == 'POST':
        try:
            eml = request.POST.get('email', None)
            pwd = request.POST.get('password', None)
            type = request.session['user']
            # return HttpResponse(type)
            if type == 'employee':
                data = {'em_email': eml}
                emData = get_info(settings.SERVER_URL + "/getEmployeeByEmail", data)
                result = emData.get('result_code')
                if result == '0':
                    data = emData.get('employee_info')
                    em_email = data[0]['em_email']
                    em_password = data[0]['em_password']
                    if pwd == em_password:
                        request.session['em_email'] = em_email         ############################################
                        request.session['pro_email'] = ''
                        request.session['pro_id'] = ''
                        request.session['manager_email'] = ''
                        request.session['manager_id'] = ''
                        employees = Employee.objects.filter(email=em_email, password=em_password)
                        if employees.count() == 0:
                            employee = Employee()
                            employee.em_id = data[0]['em_id']
                            employee.adminID = data[0]['adminID']
                            employee.name = data[0]['em_name']
                            employee.email = data[0]['em_email']
                            employee.image = data[0]['em_image']
                            employee.password = data[0]['em_password']
                            employee.gender = data[0]['em_gender']
                            employee.millennial = data[0]['em_millennial']
                            employee.givenbuck = data[0]['em_givenbuck']
                            employee.usedbuck = data[0]['em_usedbuck']
                            employee.interaction = data[0]['em_interaction']
                            if employee.interaction == '':
                                employee.interaction = '0'
                            employee.company = data[0]['adminCompany']
                            employee.save()
                            request.session['em_company'] = employee.company
                            request.session['em_adminID'] = employee.adminID
                        else:
                            employee = employees[0]
                            employee.em_id = data[0]['em_id']
                            employee.adminID = data[0]['adminID']
                            employee.name = data[0]['em_name']
                            employee.email = data[0]['em_email']
                            employee.image = data[0]['em_image']
                            employee.password = data[0]['em_password']
                            employee.gender = data[0]['em_gender']
                            employee.millennial = data[0]['em_millennial']
                            employee.givenbuck = data[0]['em_givenbuck']
                            employee.usedbuck = data[0]['em_usedbuck']
                            employee.interaction = data[0]['em_interaction']
                            if employee.interaction == '':
                                employee.interaction = '0'
                            employee.company = data[0]['adminCompany']
                            employee.save()
                            request.session['em_company'] = employee.company
                            request.session['em_adminID'] = employee.adminID
                        context = {'registered':'false'}
                        users = get_info(settings.SERVER_URL + "/getUserProfile", {'email': eml})
                        result_code = users['result_code']
                        if result_code == '0':
                            userInfo = users['user_profile']
                            if eml == userInfo[0]['email']:
                                context = {'registered':'true'}
                        return render(request, 'vacay/login_survey.html', context)
                    else:
                        return render(request, 'vacay/user_login.html', {'note': 'login failed'})
                else:
                    return render(request, 'vacay/user_login.html', {'note': 'login failed'})
            elif type == 'provider':
                data = {'proEmail': eml}
                proData = get_info(settings.SERVER_URL + "/getProviderByProEmail", data)
                result = proData.get('result_code')
                if result == '0':
                    data = proData.get('provider_info')
                    pro_email = data[0]['proEmail']
                    pro_password = data[0]['proPassword']
                    if pwd == pro_password:
                        request.session['pro_email'] = pro_email  #####################################################################
                        request.session['em_email'] = ''
                        request.session['em_company'] = ''
                        request.session['em_adminID'] = ''
                        request.session['manager_email'] = ''
                        request.session['manager_id'] = ''
                        providers = Provider.objects.filter(proEmail=pro_email, proPassword=pro_password)
                        if providers.count() == 0:
                            provider = Provider()
                            provider.proid = data[0]['proid']
                            provider.adminID = data[0]['adminID']
                            provider.proFirstName = data[0]['proFirstName']
                            provider.proLastName = data[0]['proLastName']
                            provider.proEmail = data[0]['proEmail']
                            provider.proProfileImageUrl = data[0]['proProfileImageUrl']
                            provider.proPassword = data[0]['proPassword']
                            provider.proCity = data[0]['proCity']
                            provider.proCompany = data[0]['proCompany']
                            provider.proAddress = data[0]['proAddress']
                            provider.proToken = data[0]['proToken']

                            provider.proPhone = data[0]['proPhone']
                            provider.proServicePercent = data[0]['proServicePercent']
                            provider.proProductSalePercent = data[0]['proProductSalePercent']
                            provider.proAvailable = data[0]['proAvailable']
                            provider.proSalary = data[0]['proSalary']
                            provider.save()
                            request.session['pro_id'] = provider.proid     ############################################################
                        else:
                            provider = providers[0]
                            provider.proid = data[0]['proid']
                            provider.adminID = data[0]['adminID']
                            provider.proFirstName = data[0]['proFirstName']
                            provider.proLastName = data[0]['proLastName']
                            provider.proEmail = data[0]['proEmail']
                            provider.proProfileImageUrl = data[0]['proProfileImageUrl']
                            provider.proPassword = data[0]['proPassword']
                            provider.proCity = data[0]['proCity']
                            provider.proCompany = data[0]['proCompany']
                            provider.proAddress = data[0]['proAddress']
                            provider.proToken = data[0]['proToken']
                            provider.proPhone = data[0]['proPhone']
                            provider.proServicePercent = data[0]['proServicePercent']
                            provider.proProductSalePercent = data[0]['proProductSalePercent']
                            provider.proAvailable = data[0]['proAvailable']
                            provider.proSalary = data[0]['proSalary']
                            provider.save()
                            request.session[
                                'pro_id'] = provider.proid  ############################################################
                        return render(request, 'vacay/provider_home.html', {'me':provider})
                    else:
                        return render(request, 'vacay/user_login.html', {'note': 'login failed'})
                else:

                    return render(request, 'vacay/user_login.html', {'note': 'login failed'})
            else:
                return render(request, 'vacay/user_login.html')
        except:
            return render(request, 'vacay/user_login.html')

    elif request.method == 'GET':
        return render(request, 'vacay/user_login.html')

def get_info(url, data):

    response = requests.post(url, data=data)
    return response.json()

def get_GET_info(url, data):

    response = requests.get(url+"/"+data)
    return response.json()

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def to_update_profile(request):
    if request.method == 'POST':
        eml = ''
        try:
            s1 = request.POST.get('s1', '')
            s2 = request.POST.get('s2', '')
            s3 = request.POST.get('s3', '')
            s4 = request.POST.get('s4', '')
            registered = request.POST.get('registered', '')
            # s5 = request.POST.get('s5', None)
            if s1 != '' or s2 != '' or s3 != '' or s4 != '':
                user = Friend()
                if request.session['fb_email'] != '':
                    eml = request.session['fb_email']
                    user.first_name = request.session['fb_first_name']
                    user.last_name = request.session['fb_last_name']
                    user.email = request.session['fb_email']
                    user.photo_url = request.session['fb_photo']
                    user.gender = request.session['fb_gender']
                surv = ''
                if s1 != '':
                    surv = s1
                if s2 != '':
                    if surv != '':
                        surv = surv + '\n' + s2
                    else:
                        surv = s2
                if s3 != '':
                    if surv != '':
                        surv = surv + '\n' + s3
                    else:
                        surv = s3
                if s4 != '':
                    if surv != '':
                        surv = surv + '\n' + s4
                    else:
                        surv = s4

                buffers = InfoBuffer.objects.filter(email=eml)
                if buffers.count() > 0:
                    buffer = buffers[0]
                    buffer.survey = surv
                    buffer.save()
                else:
                    buffer = InfoBuffer()
                    buffer.email = eml
                    buffer.survey = surv
                    buffer.save()
                context = {}
                if request.session['fb_email'] != '':
                    context = {
                        'user': user,
                        'surv': surv,
                        'ln_job': request.session['ln_job']
                    }
                if registered == 'false':
                    return render(request, 'vacay/register_update_profile.html', context)
                else:
                    users = Friend.objects.filter(email=request.session['fb_email'])
                    me = users[0]
                    me.first_name = request.session['fb_first_name']
                    me.last_name = request.session['fb_last_name']
                    me.email = request.session['fb_email']
                    me.photo_url = request.session['fb_photo']
                    me.gender = request.session['fb_gender']
                    me.job = request.session['ln_job']
                    me.survey = surv
                    context = {
                        'user': me
                    }
                    return render(request, 'vacay/update_profile.html', context)
                # return HttpResponse(surv)
            else:
                return redirect('/logout')
        except AssertionError:
            return redirect('/logout')

    elif request.method == 'GET':
        return redirect('/logout')

def tomap(request):
    return render(request, 'vacay/map.html')

def getloc(request):
    city = request.GET['city']
    city = city.replace('+', ' ')
    eml = request.session['fb_email']
    buffers = InfoBuffer.objects.filter(email=eml)
    buf = buffers[0]
    surv = buf.survey
    users = Friend.objects.filter(email=eml)
    if users.count() > 0:
        me = users[0]
        me.first_name = request.session['fb_first_name']
        me.last_name = request.session['fb_last_name']
        me.email = request.session['fb_email']
        me.photo_url = request.session['fb_photo']
        me.gender = request.session['fb_gender']
        me.job = request.session['ln_job']
        me.survey = surv
        me.address = city
        context = {
            'user': me
        }
        return render(request, 'vacay/update_profile.html', context)
    else:
        user = Friend()
        user.first_name = request.session['fb_first_name']
        user.last_name = request.session['fb_last_name']
        user.email = request.session['fb_email']
        user.photo_url = request.session['fb_photo']
        user.gender = request.session['fb_gender']

        job = request.session['ln_job']

        context = {
            'city': city,
            'ln_job': job,
            'survey': surv,
            'user': user
        }

        return render(request, 'vacay/register_update_profile.html', context)
        # return HttpResponse(city)


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def user_post_profile(request):
    eml = ''
    picture = ''
    name = ''
    email = ''
    company = ''
    department = ''
    millennial = ''
    if request.method == 'POST':
        job = request.POST.get('job', '')
        city = request.POST.get('city', '')
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')
        datingpref = request.POST.get('datingpref', '')
        education = request.POST.get('education', '')
        cardnum = request.POST.get('cardnum', '')
        cardcvc = request.POST.get('cardcvc', '')
        cardexpmonth = request.POST.get('cardexpmonth', '')
        cardexpyear = request.POST.get('cardexpyear', '')

 #       if cardnum == '' or cardcvc == '' or cardexpyear == '' or cardexpmonth == '':
 #           return render(request, 'vacay/result.html', {'response':'Please register your payment card info.'})

        if request.session['fb_email'] != '':
            single = request.POST.get('single', '')
            relationship = request.POST.get('relationship', '')
            newborn = request.POST.get('newborn', '')
            kids = request.POST.get('kids', '')
            dogs = request.POST.get('dogs', '')
            if single != '':
                department = single
            if relationship != '':
                if department != '':
                    department = department + '\n' + relationship
                else:
                    department = relationship
            if newborn != '':
                if department != '':
                    department = department + '\n' + newborn
                else:
                    department = newborn
            if kids != '':
                if department != '':
                    department = department + '\n' + kids
                else:
                    department = kids
            if dogs != '':
                if department != '':
                    department = department + '\n' + dogs
                else:
                    department = dogs
        if department == '': return render(request, 'vacay/result.html', {'response':'Please select your info.'})

        run = request.POST.get('run', '')
        golf = request.POST.get('golf', '')
        tennis = request.POST.get('tennis', '')
        ski = request.POST.get('ski', '')
        biking = request.POST.get('biking', '')
        fishing = request.POST.get('fishing', '')
        surfing = request.POST.get('surfing', '')
        exploring = request.POST.get('exploring', '')

        rwalk = request.POST.get('walk', '')
        r30mins = request.POST.get('30mins', '')
        r1mile = request.POST.get('1mile', '')
        r5miles = request.POST.get('5miles', '')
        r10miles = request.POST.get('10miles', '')

        gbeginner = request.POST.get('beginner', '')
        gintermediate = request.POST.get('intermediate', '')
        gadvanced = request.POST.get('advanced', '')
        gscramble = request.POST.get('scramble', '')

        t3p = request.POST.get('3p', '')
        t4p = request.POST.get('4p', '')
        t5p = request.POST.get('5p', '')
        t6p = request.POST.get('6p', '')
        twtf = request.POST.get('wtf', '')

        shot = request.POST.get('hot', '')
        sbunny = request.POST.get('bunny', '')
        sgreens = request.POST.get('greens', '')
        sblues = request.POST.get('blues', '')
        sblacks = request.POST.get('blacks', '')
        sdouble = request.POST.get('double', '')
        snotafraid = request.POST.get('notafraid', '')

        bshort = request.POST.get('short', '')
        blong = request.POST.get('long', '')
        bmountain = request.POST.get('mountain', '')
        broad = request.POST.get('road', '')

        ffly = request.POST.get('fly', '')
        flake = request.POST.get('lake', '')
        focean = request.POST.get('ocean', '')

        surocean = request.POST.get('oceansurfing', '')
        surlake = request.POST.get('lakesurfing', '')
        kitesurfing = request.POST.get('kitesurfing', '')

        emuseums = request.POST.get('museums', '')
        ecitytours = request.POST.get('citytours', '')
        enature = request.POST.get('nature', '')
        eart = request.POST.get('art', '')
        econcerts = request.POST.get('concerts', '')
        electures = request.POST.get('lectures', '')

        data = []

        if run != '':
            runList = []
            if rwalk != '' and rwalk is not None:
                runList.append(rwalk)
            if r30mins != '' and r30mins is not None:
                runList.append(r30mins)
            if r1mile != '' and r1mile is not None:
                runList.append(r1mile)
            if r5miles != '' and r5miles is not None:
                runList.append(r5miles)
            if r10miles != '' and r10miles is not None:
                runList.append(r10miles)
            if len(runList) > 0:
                runObj = {
                    "Run":str(runList).replace('\'', '')
                }
                data.append(runObj)

                # return HttpResponse(json.dumps(runObj))

        if golf != '':
            golfList = []
            if gbeginner != '' and gbeginner is not None:
                golfList.append(gbeginner)
            if gintermediate != '' and gintermediate is not None:
                golfList.append(gintermediate)
            if gadvanced != '' and gadvanced is not None:
                golfList.append(gadvanced)
            if gscramble != '' and gscramble is not None:
                golfList.append(gscramble)
            if len(golfList) > 0:
                golfObj = {
                    "Golf":str(golfList).replace('\'', '')
                }
                data.append(golfObj)

        if tennis != '':
            tennisList = []
            if t3p != '' and t3p is not None:
                tennisList.append(t3p)
            if t4p != '' and t4p is not None:
                tennisList.append(t4p)
            if t5p != '' and t5p is not None:
                tennisList.append(t5p)
            if t6p != '' and t6p is not None:
                tennisList.append(t6p)
            if twtf != '' and twtf is not None:
                tennisList.append(twtf)
            if len(tennisList) > 0:
                tennisObj = {
                    "Tennis":str(tennisList).replace('\'', '')
                }
                data.append(tennisObj)

        if ski != '':
            skiList = []
            if shot != '' and shot is not None:
                skiList.append(shot)
            if sbunny != '' and sbunny is not None:
                skiList.append(sbunny)
            if sgreens != '' and sgreens is not None:
                skiList.append(sgreens)
            if sblues != '' and sblues is not None:
                skiList.append(sblues)
            if sblacks != '' and sblacks is not None:
                skiList.append(sblacks)
            if sdouble != '' and sdouble is not None:
                skiList.append(sdouble)
            if snotafraid != '' and snotafraid is not None:
                skiList.append(snotafraid)
            if len(skiList) > 0:
                skiObj = {
                    "Ski & Snowboard":str(skiList).replace('\'', '').replace('Lodgeskier', 'Lodge\'skier\'')
                }
                data.append(skiObj)

        if biking != '':
            bikingList = []
            if bshort != '' and bshort is not None:
                bikingList.append(bshort)
            if blong != '' and blong is not None:
                bikingList.append(blong)
            if bmountain != '' and bmountain is not None:
                bikingList.append(bmountain)
            if broad != '' and broad is not None:
                bikingList.append(broad)
            if len(bikingList) > 0:
                bikingObj = {
                    "Biking":str(bikingList).replace('\'', '')
                }
                data.append(bikingObj)

        if fishing != '':
            fishingList = []
            if ffly != '' and ffly is not None:
                fishingList.append(ffly)
            if flake != '' and flake is not None:
                fishingList.append(flake)
            if focean != '' and focean is not None:
                fishingList.append(focean)
            if len(fishingList) > 0:
                fishingObj = {
                    "Fishing":str(fishingList).replace('\'', '')
                }
                data.append(fishingObj)

        if surfing != '':
            surfingList = []
            if surocean != '' and surocean is not None:
                surfingList.append(surocean)
            if surlake != '' and surlake is not None:
                surfingList.append(surlake)
            if kitesurfing != '' and kitesurfing is not None:
                surfingList.append(kitesurfing)
            if len(surfingList) > 0:
                surfingObj = {
                    "Surfing/Kitesurfing":str(surfingList).replace('\'', '')
                }
                data.append(surfingObj)

        if exploring != '':
            exploringList = []
            if emuseums != '' and emuseums is not None:
                exploringList.append(emuseums)
            if ecitytours != '' and ecitytours is not None:
                exploringList.append(ecitytours)
            if enature != '' and enature is not None:
                exploringList.append(enature)
            if eart != '' and eart is not None:
                exploringList.append(eart)
            if econcerts != '' and econcerts is not None:
                exploringList.append(econcerts)
            if electures != '' and electures is not None:
                exploringList.append(electures)
            if len(exploringList) > 0:
                exploringObj = {
                    "Exploring":str(exploringList)
                        .replace('\'', '')
                }
                data.append(exploringObj)

        if len(data) == 0: return render(request, 'vacay/result.html', {'response':'Please select your interests.'})
        interests = json.dumps(data).replace('[{\"', '{\"').replace('}]', '}').replace('},', ',').replace(', {', ',').replace(': \"', ':\"')

        if request.session['fb_email'] != '':
            eml = request.session['fb_email']
            picture = request.session['fb_photo']
            name = request.session['fb_first_name'] + ' ' + request.session['fb_last_name']
            email = eml

        nameStr = name.split()

        first_name = nameStr[0]
        try:
            last_name = nameStr[1]
        except:
            last_name = ''

        bufs = InfoBuffer.objects.filter(email=eml)
        if bufs.count() > 0:
            buf = bufs[0]
            survey = buf.survey

            if request.session['fb_email'] != '':
                users = Friend.objects.filter(email=request.session['fb_email'])
                if users.count() == 0:
                    user = Friend()
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.age = age
                    user.gender = gender
                    user.datingpref = datingpref
                    user.address = city
                    user.job = job
                    user.education = education
                    user.interests = interests
                    user.relationship = department
                    user.place_name = company
                    user.em_millennial = millennial
                    user.user_lat = '0.0'
                    user.user_lon = '0.0'
                    user.photo_url = picture
                    user.survey = survey
                    user.card_number = cardnum
                    user.card_cvc = cardcvc
                    user.card_expmonth = cardexpmonth
                    user.card_expyear = cardexpyear

                    try:
                        videofile = request.FILES['video']
                        fs = FileSystemStorage()
                        filename = fs.save(videofile.name, videofile)
                        video_url = fs.url(filename)
                        user.video = settings.URL + video_url
                    except MultiValueDictKeyError or FileNotFoundError:
                        print("File Not Exist")

                    user.save()

                    return redirect('/home')

        return redirect('/logout')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def update_profile(request):
    eml = ''
    picture = ''
    name = ''
    email = ''
    company = ''
    millennial = ''
    if request.method == 'POST':
        job = request.POST.get('job', '')
        city = request.POST.get('city', '')
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')
        datingpref = request.POST.get('datingpref', '')
        education = request.POST.get('education', '')
        cardnum = request.POST.get('cardnum', '')
        cardcvc = request.POST.get('cardcvc', '')
        cardexpmonth = request.POST.get('cardexpmonth', '')
        cardexpyear = request.POST.get('cardexpyear', '')

        interests = request.POST.get('intrsts', '')
        department = request.POST.get('inf', '')

        if request.session['fb_email'] != '':
            single = request.POST.get('single', '')
            relationship = request.POST.get('relationship', '')
            newborn = request.POST.get('newborn', '')
            kids = request.POST.get('kids', '')
            dogs = request.POST.get('dogs', '')
            if single != '':
                department = single
            if relationship != '':
                if department != '':
                    department = department + '\n' + relationship
                else:
                    department = relationship
            if newborn != '':
                if department != '':
                    department = department + '\n' + newborn
                else:
                    department = newborn
            if kids != '':
                if department != '':
                    department = department + '\n' + kids
                else:
                    department = kids
            if dogs != '':
                if department != '':
                    department = department + '\n' + dogs
                else:
                    department = dogs

        run = request.POST.get('run', '')
        golf = request.POST.get('golf', '')
        tennis = request.POST.get('tennis', '')
        ski = request.POST.get('ski', '')
        biking = request.POST.get('biking', '')
        fishing = request.POST.get('fishing', '')
        surfing = request.POST.get('surfing', '')
        exploring = request.POST.get('exploring', '')

        rwalk = request.POST.get('walk', '')
        r30mins = request.POST.get('30mins', '')
        r1mile = request.POST.get('1mile', '')
        r5miles = request.POST.get('5miles', '')
        r10miles = request.POST.get('10miles', '')

        gbeginner = request.POST.get('beginner', '')
        gintermediate = request.POST.get('intermediate', '')
        gadvanced = request.POST.get('advanced', '')
        gscramble = request.POST.get('scramble', '')

        t3p = request.POST.get('3p', '')
        t4p = request.POST.get('4p', '')
        t5p = request.POST.get('5p', '')
        t6p = request.POST.get('6p', '')
        twtf = request.POST.get('wtf', '')

        shot = request.POST.get('hot', '')
        sbunny = request.POST.get('bunny', '')
        sgreens = request.POST.get('greens', '')
        sblues = request.POST.get('blues', '')
        sblacks = request.POST.get('blacks', '')
        sdouble = request.POST.get('double', '')
        snotafraid = request.POST.get('notafraid', '')

        bshort = request.POST.get('short', '')
        blong = request.POST.get('long', '')
        bmountain = request.POST.get('mountain', '')
        broad = request.POST.get('road', '')

        ffly = request.POST.get('fly', '')
        flake = request.POST.get('lake', '')
        focean = request.POST.get('ocean', '')

        surocean = request.POST.get('oceansurfing', '')
        surlake = request.POST.get('lakesurfing', '')
        kitesurfing = request.POST.get('kitesurfing', '')

        emuseums = request.POST.get('museums', '')
        ecitytours = request.POST.get('citytours', '')
        enature = request.POST.get('nature', '')
        eart = request.POST.get('art', '')
        econcerts = request.POST.get('concerts', '')
        electures = request.POST.get('lectures', '')

        data = []

        if run != '':
            runList = []
            if rwalk != '' and rwalk is not None:
                runList.append(rwalk)
            if r30mins != '' and r30mins is not None:
                runList.append(r30mins)
            if r1mile != '' and r1mile is not None:
                runList.append(r1mile)
            if r5miles != '' and r5miles is not None:
                runList.append(r5miles)
            if r10miles != '' and r10miles is not None:
                runList.append(r10miles)
            if len(runList) > 0:
                runObj = {
                    "Run":str(runList).replace('\'', '')
                }
                data.append(runObj)

                # return HttpResponse(json.dumps(runObj))

        if golf != '':
            golfList = []
            if gbeginner != '' and gbeginner is not None:
                golfList.append(gbeginner)
            if gintermediate != '' and gintermediate is not None:
                golfList.append(gintermediate)
            if gadvanced != '' and gadvanced is not None:
                golfList.append(gadvanced)
            if gscramble != '' and gscramble is not None:
                golfList.append(gscramble)
            if len(golfList) > 0:
                golfObj = {
                    "Golf":str(golfList).replace('\'', '')
                }
                data.append(golfObj)

        if tennis != '':
            tennisList = []
            if t3p != '' and t3p is not None:
                tennisList.append(t3p)
            if t4p != '' and t4p is not None:
                tennisList.append(t4p)
            if t5p != '' and t5p is not None:
                tennisList.append(t5p)
            if t6p != '' and t6p is not None:
                tennisList.append(t6p)
            if twtf != '' and twtf is not None:
                tennisList.append(twtf)
            if len(tennisList) > 0:
                tennisObj = {
                    "Tennis":str(tennisList).replace('\'', '')
                }
                data.append(tennisObj)

        if ski != '':
            skiList = []
            if shot != '' and shot is not None:
                skiList.append(shot)
            if sbunny != '' and sbunny is not None:
                skiList.append(sbunny)
            if sgreens != '' and sgreens is not None:
                skiList.append(sgreens)
            if sblues != '' and sblues is not None:
                skiList.append(sblues)
            if sblacks != '' and sblacks is not None:
                skiList.append(sblacks)
            if sdouble != '' and sdouble is not None:
                skiList.append(sdouble)
            if snotafraid != '' and snotafraid is not None:
                skiList.append(snotafraid)
            if len(skiList) > 0:
                skiObj = {
                    "Ski & Snowboard":str(skiList).replace('\'', '').replace('Lodgeskier', 'Lodge\'skier\'')
                }
                data.append(skiObj)

        if biking != '':
            bikingList = []
            if bshort != '' and bshort is not None:
                bikingList.append(bshort)
            if blong != '' and blong is not None:
                bikingList.append(blong)
            if bmountain != '' and bmountain is not None:
                bikingList.append(bmountain)
            if broad != '' and broad is not None:
                bikingList.append(broad)
            if len(bikingList) > 0:
                bikingObj = {
                    "Biking":str(bikingList).replace('\'', '')
                }
                data.append(bikingObj)

        if fishing != '':
            fishingList = []
            if ffly != '' and ffly is not None:
                fishingList.append(ffly)
            if flake != '' and flake is not None:
                fishingList.append(flake)
            if focean != '' and focean is not None:
                fishingList.append(focean)
            if len(fishingList) > 0:
                fishingObj = {
                    "Fishing":str(fishingList).replace('\'', '')
                }
                data.append(fishingObj)

        if surfing != '':
            surfingList = []
            if surocean != '' and surocean is not None:
                surfingList.append(surocean)
            if surlake != '' and surlake is not None:
                surfingList.append(surlake)
            if kitesurfing != '' and kitesurfing is not None:
                surfingList.append(kitesurfing)
            if len(surfingList) > 0:
                surfingObj = {
                    "Surfing/Kitesurfing":str(surfingList).replace('\'', '')
                }
                data.append(surfingObj)

        if exploring != '':
            exploringList = []
            if emuseums != '' and emuseums is not None:
                exploringList.append(emuseums)
            if ecitytours != '' and ecitytours is not None:
                exploringList.append(ecitytours)
            if enature != '' and enature is not None:
                exploringList.append(enature)
            if eart != '' and eart is not None:
                exploringList.append(eart)
            if econcerts != '' and econcerts is not None:
                exploringList.append(econcerts)
            if electures != '' and electures is not None:
                exploringList.append(electures)
            if len(exploringList) > 0:
                exploringObj = {
                    "Exploring":str(exploringList)
                        .replace('\'', '')
                }
                data.append(exploringObj)

        if len(data) > 0:
            interests = json.dumps(data).replace('[{\"', '{\"').replace('}]', '}').replace('},', ',').replace(', {', ',').replace(': \"', ':\"')

        if request.session['fb_email'] != '':
            eml = request.session['fb_email']
            picture = request.session['fb_photo']
            name = request.session['fb_first_name'] + ' ' + request.session['fb_last_name']
            email = eml

        nameStr = name.split()

        first_name = nameStr[0]
        try:
            last_name = nameStr[1]
        except:
            last_name = ''

        bufs = InfoBuffer.objects.filter(email=eml)
        if bufs.count() > 0:
            buf = bufs[0]
            survey = buf.survey

            if request.session['fb_email'] != '':
                users = Friend.objects.filter(email=request.session['fb_email'])
                if users.count() > 0:
                    user = users[0]
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.age = age
                    user.gender = gender
                    user.datingpref = datingpref
                    user.address = city
                    user.job = job
                    user.education = education
                    user.interests = interests
                    user.relationship = department
                    user.place_name = company
                    user.em_millennial = millennial
                    user.user_lat = '0.0'
                    user.user_lon = '0.0'
                    user.photo_url = picture
                    user.survey = survey
                    user.card_number = cardnum
                    user.card_cvc = cardcvc
                    user.card_expmonth = cardexpmonth
                    user.card_expyear = cardexpyear

                    try:
                        videofile = request.FILES['video']
                        fs = FileSystemStorage()
                        filename = fs.save(videofile.name, videofile)
                        video_url = fs.url(filename)
                        user.video = settings.URL + video_url
                    except MultiValueDictKeyError or FileNotFoundError:
                        print("File Not Exist")

                    user.save()

                    return redirect('/home')

        return redirect('/logout')


def post_info(url, data):

    response = requests.post(url, data=data)

    return response.json()

def home(request):
    if request.session['fb_email'] != '':
        email = request.session['fb_email']
        users = Friend.objects.filter(email=email)
        if users.count() > 0:
            return render(request, 'vacay/home_common.html', {'me_email': email, 'common':'true'})
        else:
            return redirect('/logout')
    else:
        return redirect('/logout')

def get_notifications(request):
    eml = ''
    if request.session['fb_email'] != '':
        eml = request.session['fb_email']
    return render(request, 'vacay/notification.html', {'me_email': eml})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def chat_page(request):
    if request.method == 'POST':
        friend_email = request.POST.get('friend_email', None)
        friend_name = request.POST.get('friend_name', None)
        friend_photo = request.POST.get('friend_photo', None)
        if not '.com' in friend_email:
            friend_email = friend_email.replace('ddoott', '.') + '.com'
        request.session['friend_email'] = friend_email
        request.session['friend_name'] = friend_name
        request.session['friend_photo'] = friend_photo
        request.session['mode'] = 'chat'

        users = Friend.objects.filter(email=request.session['fb_email'])
        me = users[0]
        friend = Friend()
        nameStr = friend_name.split()

        first_name = nameStr[0]
        try:
            last_name = nameStr[1]
        except:
            last_name = ''
        friend.first_name = first_name
        friend.last_name = last_name
        friend.email = friend_email
        friend.photo_url = friend_photo
        createContFriend(me.email, friend_name, friend_email, friend_photo)

        return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})

    elif request.method == 'GET':
        friend_email = request.session['friend_email']

        users = Friend.objects.filter(email=request.session['fb_email'])
        me = users[0]
        users = Friend.objects.filter(email=friend_email)
        friend = users[0]
        createContFriend(me.email, friend.first_name + ' ' + friend.last_name, friend_email, friend.photo_url)

        return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})

def chat_contactor(request, contactor_id):
    contactor = ContFriend.objects.get(id=contactor_id)

    friend_email = contactor.email
    # return HttpResponse(friend_email)
    friend_name = contactor.name
    friend_photo = contactor.photo

    request.session['friend_email'] = friend_email
    request.session['friend_name'] = friend_name
    request.session['friend_photo'] = friend_photo

    friend = Friend()
    nameStr = friend_name.split()

    first_name = nameStr[0]
    try:
        last_name = nameStr[1]
    except:
        last_name = ''
    friend.first_name = first_name
    friend.last_name = last_name
    friend.email = friend_email
    friend.photo_url = friend_photo
    eml = ''
    if request.session['fb_email'] != '':
        eml = request.session['fb_email']
        users = Friend.objects.filter(email=eml)
        me = users[0]
        createContFriend(me.email, friend_name, friend_email, friend_photo)
        request.session['mode'] = 'chat'
        return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
    else:
        return redirect('/home')


def get_all_users(request):
    userList = []
    users = Friend.objects.all().order_by('-id')
    if users.count() > 0:
        for user in users:
           if user.email != request.session['fb_email']:
                user.interests = "-" + user.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                                     "\n-").replace(
                    "\"", "").replace("[", "").replace("]", "")
                user.relationship = '-' + user.relationship.replace('common', '').replace('\n', '\n-')
                userList.append(user)

    return render(request, 'vacay/friends.html', {'friends': userList})

def contactors(request):
    contactors = []
    if request.session['fb_email'] !='':
        contactors = ContFriend.objects.filter(user_email=request.session['fb_email']).order_by('-id')
    return render(request, 'vacay/contactors.html', {'contactors':contactors})

def friend_profile_mail(request, friend_id):
    user = Friend.objects.get(id=friend_id)
    user.interests = "-" + user.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                         "\n-").replace(
        "\"", "").replace("[", "").replace("]", "")
    user.relationship = '-' + user.relationship.replace('\ncommon', 'common').replace('\n', '\n-')
    return render(request, 'vacay/user_profile.html', {'friend': user, 'mail': 'true'})


def friend_profile_chat(request, friend_id):
    user = Friend.objects.get(id=friend_id)
    user.interests = "-" + user.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                         "\n-").replace(
        "\"", "").replace("[", "").replace("]", "")
    user.relationship = '-' + user.relationship.replace('\ncommon', 'common').replace('\n', '\n-')
    return render(request, 'vacay/user_profile.html', {'friend': user, 'chat':'true'})

def friendprofile(request, mail_id):
    mail = MailBox.objects.get(id=mail_id)
    email = mail.from_mail
    users = Friend.objects.filter(email=email)
    user = users[0]
    user.interests = "-" + user.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                         "\n-").replace(
        "\"", "").replace("[", "").replace("]", "")
    user.relationship = '-' + user.relationship.replace('\ncommon', 'common').replace('\n', '\n-')
    return render(request, 'vacay/friendprofile.html', {'friend': user})

def profile(request, info_id):
    tips = Watercooler.objects.get(id=info_id)
    name = tips.name
    email = tips.email
    photo = tips.photo
    users = Friend.objects.filter(email=email)
    user = users[0]
    user.interests = "-" + user.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                         "\n-").replace(
        "\"", "").replace("[", "").replace("]", "")
    user.relationship = '-' + user.relationship.replace('\ncommon', 'common').replace('\n', '\n-')
    return render(request, 'vacay/friendprofile.html', {'friend': user})

def userloc(request):
    address = request.GET['address']
    address = address.replace('+', ' ')
    return render(request, 'vacay/map_profile.html', {'address': address})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def match_friend(request):
    if request.method == 'POST':
        mode = request.POST.get('mode', None)
        name = request.POST.get('name', None)
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        photo = request.POST.get('photo', None)
        email = request.POST.get('email', None)
        gender = request.POST.get('gender', None)
        datingpref = request.POST.get('datingpref', None)
        age = request.POST.get('age', None)
        city = request.POST.get('city', None)
        job = request.POST.get('job', None)
        education = request.POST.get('education', None)
        interests = request.POST.get('interests', None)
        survey = request.POST.get('survey', None)
        request.session['mode'] = mode
        if mode == 'mail':
            friend = Friend()
            friend.first_name = first_name
            friend.last_name = last_name
            friend.email = email
            friend.photo_url = photo
            friend.age = age
            friend.gender = gender
            friend.datingpref = datingpref
            friend.address = city
            friend.education = education
            friend.job = job
            friend.interests = interests
            friend.survey = survey
            eml = ''
            if request.session['fb_email'] != '':
                eml = request.session['fb_email']
            users = Friend.objects.filter(email=eml)
            me = users[0]
            me.interests = "-" + me.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                                    "\n-").replace(
                "\"", "").replace("[", "").replace("]", "")
            request.session['friend_name'] = friend.first_name + ' ' + friend.last_name
            request.session['friend_email'] = friend.email
            request.session['friend_photo'] = friend.photo_url
            return render(request, 'vacay/friend_match.html', {'me': me, 'friend': friend})

        elif mode == 'chat':
            friend = Friend()
            friend.first_name = first_name
            friend.last_name = last_name
            friend.email = email
            friend.photo_url = photo
            eml = ''
            if request.session['fb_email'] != '':
                eml = request.session['fb_email']
            users = Friend.objects.filter(email=eml)
            me = users[0]
            request.session['friend_name'] = friend.first_name + ' ' + friend.last_name
            request.session['friend_email'] = friend.email
            request.session['friend_photo'] = friend.photo_url

            createContFriend(me.email, request.session['friend_name'], request.session['friend_email'], request.session['friend_photo'])

            return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
        else:
            return redirect('/get_all_users')

    elif request.method == 'GET':
        friend_email = request.session['friend_email']
        mode = request.session['mode']
        if mode == 'chat':
            users = Friend.objects.filter(email=friend_email)
            friend = users[0]
            eml = ''
            if request.session['em_email'] != '':
                eml = request.session['em_email']
            elif request.session['fb_email'] != '':
                eml = request.session['fb_email']
            users = Friend.objects.filter(email=eml)
            me = users[0]
            request.session['friend_name'] = friend.first_name + ' ' + friend.last_name
            request.session['friend_email'] = friend.email
            request.session['friend_photo'] = friend.photo_url

            createContFriend(me.email, request.session['friend_name'], request.session['friend_email'],
                             request.session['friend_photo'])

            return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
        else:
            return redirect('/get_all_users')

def mail_inbox(request):
    if request.session['fb_email'] != '':
        eml = request.session['fb_email']
        mails = MailBox.objects.filter(to_mail=eml).order_by('-id')
        return render(request, 'vacay/mailbox.html', {'mails':mails})
    else:
        return redirect('/get_all_users')

def mail_detail(request, mail_id):
    eml = ''
    user = Friend()
    if request.session['fb_email'] != '':
        eml = request.session['fb_email']
        users = Friend.objects.filter(email=eml)
        user = users[0]
    inbox = MailBox.objects.get(id=mail_id)
    return render(request, 'vacay/mail_detail.html', {'mail':inbox, 'me':user})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def requested_loc(request):
    if request.method == 'POST':
        lat = request.POST.get('lat', None)
        lng = request.POST.get('lng', None)
        mail_id = request.POST.get('mail_id', None)
        # lat = '40.714224'
        # lng = '-73.961452'
        if lat != '' and lat != '0.0' and lng != '' and lng != '0.0':
            # return HttpResponse(lat)
            addr = decode_coordinates_to_address(lat, lng)
            return render(request, 'vacay/map_requested.html', {'lat':lat, 'lng':lng, 'address':addr})
        else:
            return render(request, 'vacay/result.html', {'response':'No exists requested location'})
    else:
        return redirect('/mail_inbox')

def decode_coordinates_to_address(lat, lng):

    url = 'http://maps.google.com/maps/api/geocode/json?latlng=' + lat + ',' + lng + '&sensor=true/false'
    response = urllib.request.urlopen(url)
    a = response.read()
    encoding = response.info().get_content_charset('utf8')
    data = json.loads(a.decode(encoding))
    try:
        dt = data["results"][0]["formatted_address"]
        return dt
    except:
        return None

def view_mailimage(request, mail_id):
    mail = MailBox.objects.get(id=mail_id)
    image = mail.image_message_url
    return render(request, 'vacay/view_mailimage.html', {'image': image})

def reply_mail(request, mail_id):
    mail = MailBox.objects.get(id=mail_id)
    request.session['friend_email'] = mail.from_mail
    request.session['friend_photo'] = mail.photo_url

    return render(request, 'vacay/mail_compose.html',
                              {'friend_email': mail.from_mail, 'friend_photo': mail.photo_url})

def sent_mail(request):
    mails = MailBox.objects.filter(from_mail=request.session['fb_email']).order_by('-id')
    return render(request, 'vacay/sent_mail.html', {'mails':mails})

def sentmail_detail(request, mail_id):
    mail = MailBox.objects.get(id=mail_id)
    return render(request, 'vacay/sent_mail_detail.html', {'mail': mail})

def deletemail(request, mail_id):
    MailBox.objects.get(id=mail_id).delete()
    return redirect('/sent_mail')

def deletebox(request, mail_id):
    MailBox.objects.get(id=mail_id).delete()
    return redirect('/sentbox')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def sentrequested_loc(request):
    if request.method == 'POST':
        lat = request.POST.get('lat', None)
        lng = request.POST.get('lng', None)
        mail_id = request.POST.get('mail_id', None)
        # lat = '40.714224'
        # lng = '-73.961452'
        if lat != '' and lat != '0.0' and lng != '' and lng != '0.0':
            # return HttpResponse(lat)
            addr = decode_coordinates_to_address(lat, lng)
            return render(request, 'vacay/map_requested.html', {'lat':lat, 'lng':lng, 'address':addr})
        else:
            return render(request, 'vacay/result.html', {'response': 'No exists requested location'})
    else:
        return redirect('/sent_mail')

def view_sentmailimage(request, mail_id):
    mail = MailBox.objects.get(id=mail_id)
    image = mail.image_message_url
    return render(request, 'vacay/view_mailimage.html', {'image': image})

def mail_compose(request):
    friend_email = request.session['friend_email']
    friend_photo = request.session['friend_photo']
    if friend_email != '' and friend_photo != '':
        return render(request, 'vacay/mail_compose.html', {'friend_email': friend_email, 'friend_photo':friend_photo})
    else:
        return redirect('/get_all_users')

def mailcontactor(request, contactor_id):
    contactor = ContFriend.objects.get(id=contactor_id)
    friend_email = contactor.email
    friend_name = contactor.name
    friend_photo = contactor.photo

    request.session['friend_email'] = friend_email
    request.session['friend_name'] = friend_name
    request.session['friend_photo'] = friend_photo
    if friend_email != '' and friend_photo != '':
        return render(request, 'vacay/mail_compose.html',
                      {'friend_email': friend_email, 'friend_photo': friend_photo})
    else:
        return redirect('/contactors')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def send_mail_tofriend(request):
    if request.method == 'POST':
        friend_email = request.POST.get('email', None)
        friend_photo = request.POST.get('friend_photo', None)
        me_email = ''
        me_name = ''
        me_photo = ''
        em_id = ''
        if request.session['fb_email'] != '':
            me_email = request.session['fb_email']
            users = Friend.objects.filter(email=me_email)
            me = users[0]
            me_name = me.first_name + ' ' + me.last_name
            me_photo = me.photo_url
        request_date = str(int(round(time.time() * 1000)))
        subject = request.POST.get('subject', None)
        body = request.POST.get('body', None)
        lat = request.POST.get('lat', None)
        lng = request.POST.get('lng', None)
        message = subject+'\n'+body

        if lat == 'None' or lat == '':
            lat = '0.0'
        if lng == 'None' or lng == '':
            lng = '0.0'

        mail = MailBox()
        mail.from_mail = me_email
        mail.to_mail = friend_email
        mail.text_message = message
        mail.lon_message = lng
        mail.lat_message = lat
        mail.name = me_name
        mail.photo_url = me_photo
        mail.request_date = request_date

        mail.save()

        try:
            photo = request.FILES['photo']
            fs = FileSystemStorage()
            filename = fs.save(photo.name, photo)
            uploaded_file_url = fs.url(filename)

            mail.image_message_url = settings.URL + uploaded_file_url
            mail.save()

        except MultiValueDictKeyError or FileNotFoundError:
            print("File Not Exist")

        result = makemail(me_email, friend_email, message)
        friends = Friend.objects.filter(email=friend_email)
        if friends.count() > 0:
            friend = friends[0]
            friend_name = friend.first_name + ' ' + friend.last_name
            friend_photo = friend.photo_url

            createContFriend(me_email, friend_name, friend_email, friend_photo)

        return render(request, 'vacay/mail_compose.html',
                      {'friend_email': friend_email, 'friend_photo': friend_photo,
                       'success': 'true'})
    else:
        return redirect('/get_all_users')

def createContFriend(me_email, friend_name, friend_email, friend_photo):
    contfriends = ContFriend.objects.filter(email=friend_email)
    if contfriends.count() == 0:
        contfriend = ContFriend()
        contfriend.user_email = me_email
        contfriend.name = friend_name
        contfriend.email = friend_email
        contfriend.photo = friend_photo
        contfriend.save()
    else:
        contfriends[0].delete()
        contfriend = ContFriend()
        contfriend.user_email = me_email
        contfriend.name = friend_name
        contfriend.email = friend_email
        contfriend.photo = friend_photo
        contfriend.save()

def makemail(from_mail, to_mail, message):
    fromaddress = from_mail
    toaddress = to_mail
    subject = 'Hi you have a message'
    body = ''

    html = """\
                    <html>
                      <head></head>
                      <body>
                      <img src="https://vacayalldays.com/static/vacay/images/vacaylogo.jpg" style="width:80px;height:80px;border-radius: 8%; margin-left:25px;"/>
                        <h3 style="margin-left:10px; color:#02839a;">VaCay mail information</h3>
                      </body>
                    </html>
                    """

    text = message

    username = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    msg = MIMEMultipart()
    msg['From'] = fromaddress
    msg['To'] = toaddress
    msg['Subject'] = subject
    # msg['Body'] = body
    # message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    # """ % (fromaddress, ", ".join(toaddress), subject, body)

    # body = MIMEText(html, 'html')
    body1 = MIMEText(html, 'html')
    body = MIMEText(text, 'plain')

    msg.attach(body1)
    msg.attach(body)

    try:
        server = smtplib.SMTP('mail.smtp2go.com', 2525)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddress, toaddress, msg.as_string())
        server.quit()

        return 0

    except:
        return 1


def post_file(url, files, data):

    response = requests.post(url, files=files, data=data)

    return response.json()

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def map_attach(request):

    if request.method == 'POST':
        subject = request.POST.get('subject', None)
        body = request.POST.get('body', None)

        if subject == 'None':
            subject = ''
        if body == 'None':
            body = ''

        context = {
            'subject': subject,
            'body': body
        }
        return render(request, 'vacay/map_attach.html', context)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def attach_loc(request):
    if request.method == 'POST':
        lat = request.POST.get('latitude', None)
        lng = request.POST.get('longitude', None)

        subject = request.POST.get('subject', None)
        body = request.POST.get('body', None)

        friend_email = request.session['friend_email']
        friend_photo = request.session['friend_photo']

        context = {
            'friend_email': friend_email,
            'friend_photo': friend_photo,
            'lat': lat,
            'lng': lng,
            'subject': subject,
            'body': body,
            'map': 'map'
        }
        if friend_email != '' and friend_photo != '':
            return render(request, 'vacay/mail_compose.html', context)
        else:
            return redirect('/get_all_users')
    else:
        friend_email = request.session['friend_email']
        friend_photo = request.session['friend_photo']

        context = {
            'friend_email': friend_email,
            'friend_photo': friend_photo
        }
        if friend_email != '' and friend_photo != '':
            return render(request, 'vacay/mail_compose.html', context)
        else:
            return redirect('/get_all_users')

def map_chat(request):
    return render(request, 'vacay/map_chat.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def submit_chatloc(request):
    if request.method == 'POST':
        lat = request.POST.get('latitude', None)
        lng = request.POST.get('longitude', None)

        # return HttpResponse(lat)

        friend_email = request.session['friend_email']
        mode = request.session['mode']
        if mode == 'chat':

            friends = Friend.objects.filter(email=friend_email)
            friend = friends[0]
            friends = Friend.objects.filter(email=request.session['fb_email'])
            me = friends[0]
            request.session['friend_email'] = friend.email
            request.session['friend_photo'] = friend.photo_url

            return render(request, 'vacay/chat.html', {'me': me, 'friend': friend, 'lat': lat, 'lng': lng})
        else:
            return redirect('/get_all_users')
    elif request.method == 'GET':
        friend_email = request.session['friend_email']
        mode = request.session['mode']
        if mode == 'chat':
            friends = Friend.objects.filter(email=friend_email)
            friend = friends[0]
            friends = Friend.objects.filter(email=request.session['fb_email'])
            me = friends[0]
            request.session['friend_email'] = friend.email
            request.session['friend_photo'] = friend.photo_url

            return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
        else:
            return redirect('/get_all_users')

def show_chatloc(request):
    latlng = request.GET['latlng']
    latlng = latlng.split("_")
    lat = latlng[0]
    lng = latlng[1]
    # lat = '40.714224'
    # lng = '-73.961452'
    if lat != '' and lat != '0.0' and lng != '' and lng != '0.0':
        # return HttpResponse(lat+"/"+lng)
        addr = decode_coordinates_to_address(lat, lng)
        # return HttpResponse(addr)
        return render(request, 'vacay/map_requested.html', {'lat': lat, 'lng': lng, 'address': addr})

def myprofile(request):
    eml = ''
    if request.session['fb_email'] != '':
        eml = request.session['fb_email']
        users = Friend.objects.filter(email=eml)
        if users.count() > 0:
            me = users[0]
            me.relationship = '-' + me.relationship.replace('\ncommon', 'common').replace('\n', '\n-')
            me.interests = "-" + me.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                                    "\n-").replace(
                "\"", "").replace("[", "").replace("]", "")
            return render(request, 'vacay/my_profile.html', {'me':me})
        else:
            return redirect('/home')
    else:
        return redirect('/home')

def proprofile(request):
    eml = request.session['pro_email']
    users = get_info(settings.SERVER_URL + "/getProviderByProEmail", {'proEmail': eml})
    result_code = users['result_code']
    if result_code == '0':
        userInfo = users['provider_info']
        me = Provider()
        me.proid = userInfo[0]['proid']
        me.adminID = userInfo[0]['adminID']
        me.proFirstName = userInfo[0]['proFirstName']
        me.proLastName = userInfo[0]['proLastName']
        me.proEmail = userInfo[0]['proEmail']
        me.proProfileImageUrl = userInfo[0]['proProfileImageUrl']
        me.proCity = userInfo[0]['proCity']
        me.proCompany = userInfo[0]['proCompany']
        me.proAddress = userInfo[0]['proAddress']
        me.proPassword = userInfo[0]['proPassword']
        me.proToken = userInfo[0]['proToken']

        return render(request, 'vacay/provider_profile.html', {'me':me})

def eat_entry(request):
    return render(request, 'vacay/eat_entry.html')

def eat(request):
    request.session['eat_type'] = 'eat'
    return render(request, 'vacay/eat_selloc.html')

def drink(request):
    request.session['eat_type'] = 'drink'
    return render(request, 'vacay/eat_selloc.html')

def denver(request):
    eatdrinks = get_denver_eatdrinkinfo()
    return render(request, 'vacay/eat_list.html', {'eatdrinks':eatdrinks, 'where':'denver'})

def get_denver_eatdrinkinfo():
    root_url = '/static/vacay/images/'
    edphotoList = ['dencru', 'denedge', 'denguard', 'denhapa', 'denlinger', 'denlola', 'denmister', 'denocean',
                   'denosteria', 'denreoja', 'densqu', 'dentherio', 'denthirsty', 'denzengo']
    ednameList = ["Cru Wine Bar", "Edge Bar", "Delarosa", "Guard and Grace", "Hapa Sushi", "Linger", "Lola",
                  "Mister Tuna", "Ocean Prime", "Osteria Marco", "Rioja", "Squeaky Bean", "The Rio", "Thirsty Lion",
                  "Zengo"]
    edtypeList = ["Napa Style Food & Wine", "Steakhouse", "Modern Steakhouse", "Sushi", "Mexican", "Mexican",
                  "New American", "Steakhouse", "Italian", "Mediterranean", "Farm and Table", "Mexican", "Modern Pub",
                  "Asian"]
    edmenuList = ['http://www.cruawinebar.com/', 'http://www.edgerestaurantdenver.com/menus/dinner_menu/',
                  'http://guardandgrace.com/', 'http://hapasushi.com/dinner', 'http://lingerdenver.com/',
                  'http://www.loladenver.com/', 'http://www.mistertuna.com/',
                  'http://www.ocean-prime.com/locations-menus/denver/menus', 'http://www.osteriamarco.com/',
                  'http://www.riojadenver.com/',
                  'http://www.thesqueakybean.com/', 'https://www.riograndemexican.com/menus/',
                  'http://www.thirstyliongastropub.com/denver/#denver-menu',
                  'http://www.richardsandoval.com/zengodenver/']
    edopentableList = ['', 'http://www.opentable.com/edge-restaurant-and-bar',
                       'http://www.opentable.com/guard-and-grace-reservations-denver?restref=115339&datetime=2016-10-23T193A00&covers=2&searchdatetime=2016-10-23T193A00&partysize=2',
                       'http://www.opentable.com/hapa-sushi-grill-and-sake-bar-cherry-creek',
                       'http://www.opentable.com/linger', '', 'http://www.opentable.com/r/mister-tuna-denver',
                       'http://www.opentable.com/ocean-prime-denver',
                       'http://www.opentable.com/osteria-marco', 'http://www.opentable.com/r/rioja-denver',
                       'http://www.opentable.com/squeaky-bean-reservations-denver',
                       'http://www.opentable.com/rio-grande-denver',
                       'http://www.opentable.com/thirsty-lion-gastropub-and-grill-denver',
                       'http://www.opentable.com/zengo-denver']
    edlocationList = [
        'https://www.google.com/maps/place/CRC39A+-+Larimer+Square+Denver/@39.803259,-104.9742341,11z/data=!4m8!1m2!2m1!1sCru+Wine+Bar+denver+map!3m4!1s0x0:0x8298f08f614b28d6!8m2!3d39.7478499!4d-104.9988699',
        'https://www.google.com/maps/place/EDGE+Restaurant+and+Bar/@39.7464955,-104.998015,15z/data=!4m5!3m4!1s0x0:0x2c84dc972d992567!8m2!3d39.7464955!4d-104.998015',
        'https://www.google.com/maps/place/Guard+and+Grace/@39.74765,-104.9897191,15z/data=!4m5!3m4!1s0x0:0xff8859bf67c1b281!8m2!3d39.74765!4d-104.9897191',
        'https://www.google.com/maps/place/Hapa+Sushi+Grill+and+Sake+Bar/@39.7192954,-104.9548047,15z/data=!4m5!3m4!1s0x0:0x4d0bcc254c5e4e83!8m2!3d39.7192954!4d-104.9548047',
        'https://www.google.com/maps/place/Linger/@39.759526,-105.0114406,15z/data=!4m5!3m4!1s0x0:0xf787e81b653c2464!8m2!3d39.759526!4d-105.0114406',
        'https://www.google.com/maps/place/Lola+Coastal+Mexican/@39.7592302,-105.0109062,15z/data=!4m5!3m4!1s0x0:0x13126077f6ea9eb3!8m2!3d39.7592302!4d-105.0109062',
        'https://www.google.com/maps/place/Mister+Tuna/@39.765416,-104.9855702,15z/data=!4m5!3m4!1s0x0:0x5e3f4e2a7b550b12!8m2!3d39.765416!4d-104.9855702',
        'https://www.google.com/maps/place/Ocean+Prime/@39.7482934,-104.999026,15z/data=!4m5!3m4!1s0x0:0x3375ad123c92f1f5!8m2!3d39.7482934!4d-104.999026',
        'https://www.google.com/maps/place/Osteria+Marco/@39.7481801,-104.9991492,15z/data=!4m5!3m4!1s0x0:0x7bd31b04293b3006!8m2!3d39.7481801!4d-104.9991492',
        'https://www.google.com/maps/place/Rioja/@39.7479473,-104.9994686,15z/data=!4m5!3m4!1s0x0:0xed9b3022813b274c!8m2!3d39.7479473!4d-104.9994686',
        'https://www.google.com/maps/place/The+Squeaky+Bean/@39.750976,-105.0017343,15z/data=!4m2!3m1!1s0x0:0x27685318a5c36cc9?sa=X&ved=0ahUKEwjUqq-uwpTQAhUNxWMKHaZTB3oQ_BIIeDAK',
        'https://www.google.com/maps/place/Rio+Grande/@39.7502288,-105.0000807,15z/data=!4m2!3m1!1s0x0:0x727e635665949cb8?sa=X&ved=0ahUKEwjArebtwJTQAhULwmMKHcxTA_wQ_BIIejAK',
        'https://www.google.com/maps/place/Thirsty+Lion+Gastropub+and+Grill+-+Union+Station/@39.7523187,-105.0009258,15z/data=!4m2!3m1!1s0x0:0x810412311c26c755?sa=X&ved=0ahUKEwizkpXMwZTQAhUTz2MKHewlCdAQ_BIIeDAK',
        'https://www.google.com/maps/place/Zengo/@39.7551309,-105.0045533,15z/data=!4m2!3m1!1s0x0:0x50dfd423bda16db0?sa=X&ved=0ahUKEwjavcGjwpTQAhVJ6WMKHTWlBU0Q_BIIfzAO']
    i = 0
    eatdrinks = []
    for editem in edphotoList:
        eatdrink = EatDrink()
        eatdrink.edrink_id = i
        eatdrink.photo = root_url + editem + '.jpg'
        eatdrink.name = ednameList[i]
        eatdrink.type = edtypeList[i]
        eatdrink.menu = edmenuList[i]
        eatdrink.opentable = edopentableList[i]
        eatdrink.location = edlocationList[i]
        eatdrinks.append(eatdrink)
        i = i + 1
    return eatdrinks

def sanfran(request):
    eatdrinks = get_sanfran_eatdrinkinfo()
    return render(request, 'vacay/eat_list.html', {'eatdrinks':eatdrinks, 'where':'sanfran'})

def get_sanfran_eatdrinkinfo():
    root_url = '/static/vacay/images/'
    edphotoList = ['sf0', 'sf1', 'sf2', 'sf3', 'sf4', 'sf5', 'sf6', 'sf7',
                   'sf8', 'sf9', 'sf10', 'sf11']
    ednameList = ["Acquerello", "Boulevard", "Delarosa", "Gary Danko", "Hog Island Oyster Co", "House of Prime Rib",
                  "La Folie", "Nopa", "Saison", "Spruce", "The House", "Tony's Pizza Napoletana"]
    edtypeList = ["Italian", "American", "Italian", "French", "New Seafood", "English",
                  "French", "New American", "New American", "American", "Asian", "Italian"]
    edmenuList = ['http://www.acquerello.com/menus/PrixFixeMenu.pdf', 'http://www.boulevardrestaurant.com/menus/#boulevard-menus',
                  'http://www.delarosasf.com/', 'http://places.singleplatform.com/gary-danko-2/menu?ref=google', 'https://hogislandoysters.com/',
                  'http://houseofprimerib.net/', 'http://www.lafolie.com/menus/#la-folie-menus3',
                  'http://www.nopasf.com/menu/dinner', 'https://www.zomato.com/san-francisco/saison-soma/menu?utm_source=Google&utm_medium=Local&utm_campaign=GoogleMenus',
                  'http://www.sprucesf.com/food_wine',
                  'http://www.thehse.com/', 'http://tonyspizzanapoletana.com/menu/']
    edopentableList = ['http://www.opentable.com/acquerello?ref=1068',
                       'http://www.opentable.com/r/boulevard-san-francisco',
                       'http://www.opentable.com/r/delarosas-downtown-san-francisco',
                       'http://www.opentable.com/gary-danko', '', 'http://www.opentable.com/san-francisco-restaurants?mn=5&ref=9859&sp=ppc_g_sf_cuis&gclid=Cj0KEQjwnKzABRDy2pb7nPSazdsBEiQAI4lZQCP0KHe-hPJly9uimsJfKJeIko5cFhj8qzcUmWaI8koaAq9C8P8HAQ',
                       'http://www.lafolie.com/menus/#la-folie-menus3',
                       'http://www.opentable.com/san-francisco/nopa-restaurants?ref=9886&sp=ppc_g_sf_hood&gclid=Cj0KEQjwnKzABRDy2pb7nPSazdsBEiQAI4lZQIIK2JPw9g53o4FNLfVxTj7hxZ6XVqpSxL3kfSdBHmcaApT78P8HAQ',
                       'http://www.opentable.com/saison-reservations-san-francisco',
                       'http://www.opentable.com/spruce',
                       '',
                       'http://www.opentable.com/r/tonys-pizza-napoletana-san-francisco']
    edlocationList = [
        'https://www.google.com/maps/place/Acquerello/@37.7915485,-122.421442,15z/data=!4m5!3m4!1s0x0:0xa5a20b813854425d!8m2!3d37.7915485!4d-122.421442',
        'https://www.google.com/maps/place/Boulevard/@37.79332,-122.392761,15z/data=!4m5!3m4!1s0x0:0x34b391d08d9fe6bc!8m2!3d37.79332!4d-122.392761',
        'https://www.google.com/maps/place/Delarosa/@37.8003028,-122.4391249,15z/data=!4m5!3m4!1s0x0:0xe1165ec97a6da48!8m2!3d37.8003028!4d-122.4391249',
        'https://www.google.com/maps/place/Restaurant+Gary+Danko/@37.8058724,-122.4206313,15z/data=!4m5!3m4!1s0x0:0x8ee57d9f647dbc1!8m2!3d37.8058724!4d-122.4206313',
        'https://www.google.com/maps/place/Hog+Island+Oyster+Co/@37.7960308,-122.3935689,15z/data=!4m5!3m4!1s0x0:0x830980e627627a81!8m2!3d37.7960308!4d-122.3935689',
        'https://www.google.com/maps/place/House+of+Prime+Rib/@37.7933928,-122.4227072,15z/data=!4m5!3m4!1s0x0:0x3ef25abd292344d9!8m2!3d37.7933928!4d-122.4227072',
        'https://www.google.com/maps/place/La+Folie/@37.798144,-122.4220082,15z/data=!4m5!3m4!1s0x0:0x88d3a2ab149fb6b4!8m2!3d37.798144!4d-122.4220082',
        'https://www.google.com/maps/place/La+Folie/@37.798144,-122.4220082,15z/data=!4m5!3m4!1s0x0:0x88d3a2ab149fb6b4!8m2!3d37.798144!4d-122.4220082',
        'https://www.google.com/maps/place/Saison/@37.7795354,-122.392263,15z/data=!4m5!3m4!1s0x0:0x77a00452793abd5c!8m2!3d37.7795354!4d-122.392263',
        'https://www.google.com/maps/place/Saison/@37.7795354,-122.392263,15z/data=!4m5!3m4!1s0x0:0x77a00452793abd5c!8m2!3d37.7795354!4d-122.392263',
        'https://www.google.com/maps/place/Saison/@37.7795354,-122.392263,15z/data=!4m5!3m4!1s0x0:0x77a00452793abd5c!8m2!3d37.7795354!4d-122.392263',
        'https://www.google.com/maps/place/Tony\'s+Pizza+Napoletana/@37.8003257,-122.408985,15z/data=!4m5!3m4!1s0x0:0xbfb3fcde3487fb40!8m2!3d37.8003257!4d122.408985']
    i = 0
    eatdrinks = []
    for editem in edphotoList:
        eatdrink = EatDrink()
        eatdrink.edrink_id = i
        eatdrink.photo = root_url + editem + '.jpg'
        eatdrink.name = ednameList[i]
        eatdrink.type = edtypeList[i]
        eatdrink.menu = edmenuList[i]
        eatdrink.opentable = edopentableList[i]
        eatdrink.location = edlocationList[i]
        eatdrinks.append(eatdrink)
        i = i + 1
    return eatdrinks

def den_eddetail(request, eatdrink_id):
    eatdrinks = get_denver_eatdrinkinfo()
    eds = []
    for eatdrink in eatdrinks:
        if eatdrink.edrink_id == int(eatdrink_id):
            eds.append(eatdrink)
    # return HttpResponse(eds[0].name)
    return render(request, 'vacay/eddetail.html', {'eatdrink':eds[0]})

def san_eddetail(request, eatdrink_id):
    eatdrinks = get_sanfran_eatdrinkinfo()
    eds = []
    for eatdrink in eatdrinks:
        if eatdrink.edrink_id == int(eatdrink_id):
            eds.append(eatdrink)
    # return HttpResponse(eds[0].name)
    return render(request, 'vacay/eddetail.html', {'eatdrink':eds[0]})

def get_jobInfo(adminID):
    jobList = []
    data = {'adminID': adminID}
    jobData = get_info(settings.SERVER_URL + "/getAllJobByAdminID", data)
    result = jobData.get('result_code')
    if result == '0':
        jobInfo = jobData.get('job_info')
        for jobinfo in jobInfo:
            job = Job()
            job.job_id = jobinfo['job_id']
            job.adminID = adminID
            job.adminlogo = jobinfo['adminLogoImageUrl']
            job.req = jobinfo['job_req']
            job.title = jobinfo['job_name']
            job.department = jobinfo['job_department']
            job.location = jobinfo['job_location']
            job.description = jobinfo['job_description']
            job.postdate = jobinfo['job_postdate']
            job.empty = jobinfo['job_empty']
            job.admincompany = jobinfo['adminCompany']
            job.survey = jobinfo['job_survey']

            jobList.insert(0, job)
        return jobList
    else:return None

def get_jobs(request):
    try:
        adminID = request.session['em_adminID']
        jobList = get_jobInfo(adminID)
        if jobList is not None:
            return render(request, 'vacay/job_list.html', {'jobs': jobList})
        else:
            return redirect('/home', {'error':'true'})

    except KeyError or AssertionError:
        try:
            eml = request.session['em_email']
            data = {'em_email': eml}
            emData = get_info(settings.SERVER_URL + "/getEmployeeByEmail", data)
            result = emData.get('result_code')
            if result == '0':
                data = emData.get('employee_info')
                adminID = data[0]['adminID']
                request.session['em_adminID'] = adminID
                jobList = get_jobInfo(adminID)
                if jobList is not None:
                    return render(request, 'vacay/job_list.html', {'jobs': jobList})
                else:
                    return redirect('/home', {'error':'true'})
            else:
                return redirect('/home', {'error':'true'})
        except AssertionError:
            return redirect('/home', {'error':'true'})

def job_detail(request, job_id):
    adminID = ''
    if request.session['em_adminID'] != '':
        adminID = request.session['em_adminID']
    elif request.session['manager_id'] != '':
        adminID = request.session['manager_id']
    adminEmail = get_em_adminEmail(adminID)
    data = {'adminID': adminID}
    jobData = get_info(settings.SERVER_URL + "/getAllJobByAdminID", data)
    result = jobData.get('result_code')
    if result == '0':
        jobInfo = jobData.get('job_info')
        for jobinfo in jobInfo:
            if job_id == jobinfo['job_id']:
                request.session['job_id'] = job_id
                job = Job()
                job.job_id = jobinfo['job_id']
                job.adminID = adminID
                job.adminlogo = jobinfo['adminLogoImageUrl']
                job.req = jobinfo['job_req']
                job.title = jobinfo['job_name']
                job.department = jobinfo['job_department']
                job.location = jobinfo['job_location']
                job.description = jobinfo['job_description']
                job.postdate = jobinfo['job_postdate']
                job.empty = jobinfo['job_empty']
                job.admincompany = jobinfo['adminCompany']
                job.survey = jobinfo['job_survey']

                if job.survey.startswith("http") and "?usp=sf_link" in job.survey:
                    job.survey = job.survey.replace("?usp=sf_link","?embedded=true")
                    return render(request, 'vacay/job_detail.html', {'job': job, 'adminEmail':adminEmail, 'survey':'true'})
                else:
                    return render(request, 'vacay/job_detail.html', {'job': job, 'adminEmail':adminEmail})
    else:return redirect('/home', {'error':'true'})

def get_em_adminEmail(data):
    adminData = get_GET_info(settings.SERVER_URL + "/getAdminData", data)
    result = adminData.get('result_code')
    if result == '0':
        adminInfo = adminData.get('adminData')
        adminEmail = adminInfo[0]['adminEmail']
        return adminEmail

def job_media(request, job_id):
    data = {
        'item_id':job_id,
        'item':'job'
    }
    jobMedia = get_info(settings.SERVER_URL + "/get_job_media", data)
    result = jobMedia.get('result_code')
    if result == '0':
        media = jobMedia.get('media')
        video = media['video_url']
        youtube = media['youtube_url']
        return render(request, 'vacay/job_media.html', {'video':video, 'youtube':youtube})
    else:
        return redirect('/job_detail_'+request.session['job_id'])

def get_announceInfo(adminID):
    announceList = []
    data = {'adminID': adminID}
    announceData = get_info(settings.SERVER_URL + "/getAllAnnounceByAdminID", data)
    result = announceData.get('result_code')
    if result == '0':
        announceInfo = announceData.get('announce_info')
        for announceinfo in announceInfo:
            announce = Announce()
            announce.an_id = announceinfo['an_id']
            announce.adminID = adminID
            announce.adminlogo = announceinfo['adminLogoImageUrl']
            announce.title = announceinfo['an_title']
            announce.audience = announceinfo['an_audience']
            announce.subject = announceinfo['an_subject']
            announce.description = announceinfo['an_description']
            announce.callofaction = announceinfo['an_callofaction']
            announce.owneremail = announceinfo['an_owneremail']
            announce.image = announceinfo['an_image']
            announce.viewnum = announceinfo['an_viewnum']
            announce.responsenum = announceinfo['an_responsenum']
            announce.admincompany = announceinfo['adminCompany']
            announce.postdate = announceinfo['an_postdate']
            announce.survey = announceinfo['an_survey']

            announceList.append(announce)
        return announceList
    else:return None

def get_announces(request):
    try:
        adminID = request.session['em_adminID']
        announceList = get_announceInfo(adminID)
        if announceList is not None:
            return render(request, 'vacay/announce_list.html', {'announces': announceList})
        else:
            return redirect('/home', {'error':'true'})

    except KeyError or AssertionError:
        try:
            eml = request.session['em_email']
            data = {'em_email': eml}
            emData = get_info(settings.SERVER_URL + "/getEmployeeByEmail", data)
            result = emData.get('result_code')
            if result == '0':
                data = emData.get('employee_info')
                adminID = data[0]['adminID']
                request.session['em_adminID'] = adminID
                announceList = get_announceInfo(adminID)
                if announceList is not None:
                    return render(request, 'vacay/announce_list.html', {'announces': announceList})
                else:
                    return redirect('/home', {'error':'true'})
            else:
                return redirect('/home', {'error':'true'})
        except AssertionError:
            return redirect('/home', {'error':'true'})

def announce_detail(request, announce_id):
    adminID = ''
    manager = ''
    if request.session['em_adminID'] != '':
        adminID = request.session['em_adminID']
        employees = Employee.objects.filter(email=request.session['em_email'])
        em_id = employees[0].em_id
        res = view_announce(announce_id, em_id, '0')
    elif request.session['manager_id'] != '':
        adminID = request.session['manager_id']
        manager = 'true'
    adminEmail = get_em_adminEmail(adminID)
    data = {'adminID': adminID}
    announceData = get_info(settings.SERVER_URL + "/getAllAnnounceByAdminID", data)
    result = announceData.get('result_code')
    if result == '0':
        announceInfo = announceData.get('announce_info')
        for announceinfo in announceInfo:
            if announceinfo['an_id'] == announce_id:
                request.session['announce_id'] = announce_id
                announce = Announce()
                announce.an_id = announceinfo['an_id']
                announce.adminID = adminID
                announce.adminlogo = announceinfo['adminLogoImageUrl']
                announce.title = announceinfo['an_title']
                announce.audience = announceinfo['an_audience']
                announce.subject = announceinfo['an_subject']
                announce.description = announceinfo['an_description']
                announce.callofaction = announceinfo['an_callofaction']
                announce.owneremail = announceinfo['an_owneremail']
                announce.image = announceinfo['an_image']
                announce.viewnum = announceinfo['an_viewnum']
                announce.responsenum = announceinfo['an_responsenum']
                announce.admincompany = announceinfo['adminCompany']
                announce.postdate = announceinfo['an_postdate']
                announce.survey = announceinfo['an_survey']

                if announce.survey.startswith("http") and "?usp=sf_link" or "?usp=pp_url" in announce.survey:
                    announce.survey = announce.survey.replace("?usp=sf_link", "?embedded=true")
                    return render(request, 'vacay/announce_detail.html',
                                  {'announce': announce, 'adminEmail': adminEmail, 'survey': 'true', 'manager': manager})
                else:
                    return render(request, 'vacay/announce_detail.html',
                                  {'announce': announce, 'adminEmail': adminEmail, 'manager': manager})
    else:
        return redirect('/home', {'error':'true'})

def announce_media(request, announce_id):
    data = {
        'item_id': announce_id,
        'item': 'announce'
    }
    announceMedia = get_info(settings.SERVER_URL + "/get_media", data)
    result = announceMedia.get('result_code')
    if result == '0':
        media = announceMedia.get('media')
        md = Media()
        md.video = media['video_url']
        md.youtube = media['youtube_url']
        md.imageA = media['image_a']
        md.imageB = media['image_b']
        md.imageC = media['image_c']
        md.imageD = media['image_d']
        md.imageE = media['image_e']
        md.imageF = media['image_f']

        return render(request, 'vacay/announce_media.html', {'media': md})
    else:
        return redirect('/announce_detail_' + request.session['announce_id'])

def view_announce(an_id, em_id, index):
    data = {
        'an_id':an_id,
        'em_id':em_id,
        'index':index
    }
    response = post_info(settings.SERVER_URL + "/updateCount", data)
    result = response.get('result_code')
    return result

def announce_signup(request, announce_id):
    employees = Employee.objects.filter(email=request.session['em_email'])
    em_id = employees[0].em_id
    res = view_announce(announce_id, em_id, '1')
    if res == '0':
        adminID = request.session['em_adminID']
        adminEmail = get_em_adminEmail(adminID)
        data = {'adminID': adminID}
        announceData = get_info(settings.SERVER_URL + "/getAllAnnounceByAdminID", data)
        result = announceData.get('result_code')
        if result == '0':
            announceInfo = announceData.get('announce_info')
            for announceinfo in announceInfo:
                if announceinfo['an_id'] == announce_id:
                    request.session['announce_id'] = announce_id
                    announce = Announce()
                    announce.an_id = announceinfo['an_id']
                    announce.adminID = adminID
                    announce.adminlogo = announceinfo['adminLogoImageUrl']
                    announce.title = announceinfo['an_title']
                    announce.audience = announceinfo['an_audience']
                    announce.subject = announceinfo['an_subject']
                    announce.description = announceinfo['an_description']
                    announce.callofaction = announceinfo['an_callofaction']
                    announce.owneremail = announceinfo['an_owneremail']
                    announce.image = announceinfo['an_image']
                    announce.viewnum = announceinfo['an_viewnum']
                    announce.responsenum = announceinfo['an_responsenum']
                    announce.admincompany = announceinfo['adminCompany']
                    announce.postdate = announceinfo['an_postdate']
                    announce.survey = announceinfo['an_survey']

                    if announce.survey.startswith("http") and "?usp=sf_link" in announce.survey:
                        announce.survey = announce.survey.replace("?usp=sf_link", "?embedded=true")
                        return render(request, 'vacay/announce_detail.html',
                                      {'announce': announce, 'adminEmail': adminEmail, 'survey': 'true', 'signed':'true'})
                    else:
                        return render(request, 'vacay/announce_detail.html',
                                      {'announce': announce, 'adminEmail': adminEmail, 'signed':'true'})
        else:
            return redirect('/home', {'error':'true'})
    else:
        return redirect('/announce_detail_' + request.session['announce_id'])

def get_watercoolerInfo(category, company):
    data = {
        'category': category,
        'company': company
    }
    response = get_info(settings.SERVER_URL + "/get_watercooler", data)
    result = response.get('result_code')
    if result == '0':
        wcList = []
        watercoolerInfo = response.get('data')
        for watercoolerinfo in watercoolerInfo:
            wc = Watercooler()
            wc.wc_id = watercoolerinfo['id']
            wc.name = watercoolerinfo['name']
            wc.category = watercoolerinfo['category']
            wc.company = watercoolerinfo['company']
            wc.content = watercoolerinfo['content']
            # wc.content = wc.content.encode('utf8', 'ignore')
            wc.link = watercoolerinfo['link'] #    watercoolerinfo['link']
            wc.photo = watercoolerinfo['photoUrl']
            wcList.insert(0, wc)
        return wcList
    else:
        return None


def get_wc(request):
    category = request.GET['category']
    request.session['wc_category'] = category
    em_company = request.session['em_company']
    data = get_watercoolerInfo(category, em_company)
    if data is not None:
        return render(request, 'vacay/watercooler_list.html', {'watercoolers':data, 'category':category})
    else:
        return redirect('/home', {'error':'true'})

def watercooler_setup(request):
    return render(request, 'vacay/watercooler_setup.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def upload_watercooler(request):
    if request.method == 'POST':
        category = request.POST.get('category', '')
        content = request.POST.get('description', '')
        link = request.POST.get('link', None)
        if request.session['fb_email'] != '':
            users = Friend.objects.filter(email=request.session['fb_email'])
            name = users[0].first_name + ' ' + users[0].last_name
            email = users[0].email
            photo = users[0].photo_url
            gender = users[0].gender
            if link is None: link = ''

            if category == '' or category is None:
                context = {'item': 'uploadwatercooler',
                           'response': 'Please select category!'}
                return render(request, 'vacay/result.html', context)
            else:

                tips = Watercooler()
                tips.name = name
                tips.email = email
                tips.photo = photo
                tips.gender = gender
                tips.company = 'common'
                tips.category = category
                tips.content = content
                tips.link = link
                tips.save()

                context = {'item': 'uploadwatercooler',
                           'response': 'Success!'}
                return render(request, 'vacay/result.html', context)

    elif request.method == 'GET':
        return redirect('/watercooler_setup')

def comments(request, wc_id):
    cmts = Comment.objects.filter(info_id=wc_id).order_by('-id')
    tips = Watercooler.objects.get(id=wc_id)
    request.session['wc_id'] = wc_id
    return render(request, 'vacay/incomments.html', {'comments': cmts, 'info': tips})

def add_wc_comment(request, wc_id):
    tips = Watercooler.objects.get(id=wc_id)
    return render(request, 'vacay/add_comment.html', {'watercooler': tips})

def drawing(request):
    text = request.GET['comment']
    request.session['wc_comment'] = text
    # return HttpResponse(text)
    return render(request, 'vacay/wc_comment_drawing.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def returnfromdrawing(request):
    if request.method == 'POST':
        imageURL = request.POST.get('image', None)
        text = request.session['wc_comment']
        if text == 'None': text = ''
        tips = Watercooler.objects.get(id=request.session['wc_id'])
        return render(request, 'vacay/add_comment.html',
                      {'watercooler': tips, 'image': imageURL, 'comment': text})
    else:
        return redirect('/add_wc_comment/' + request.session['wc_id'])

from urllib.request import urlretrieve
import base64

def wc_comment_upload(request):
    if request.method == 'POST':
        text = request.POST.get('text', None)
        image = request.POST.get('image', None)

        # url = base64.b64encode(image.encode())
        # with open("imageToSave.png", "wb") as fh:
        #     fh.write(base64.decodebytes(url))
        #     fl = fh.read()
        #     fs = FileSystemStorage()
        #     filename = fs.save(image.name, image)
        #     uploaded_file_url = fs.url(filename)
        #     return HttpResponse(uploaded_file_url)

        wc_id = request.session['wc_id']

        users = Friend.objects.filter(email=request.session['fb_email'])
        photo = users[0].photo_url
        name = users[0].first_name + ' ' + users[0].last_name
        email = users[0].email

        comment = Comment()
        comment.info_id = wc_id
        comment.photoUrl = photo
        comment.name = name
        comment.email = email
        comment.text = text
        comment.imageUrl = image

        comment.save()

        context = {'item': 'uploadwccomment',
                   'response': 'Success!'}
        return render(request, 'vacay/result.html', context)

def beauty_entry(request):
    response = post_info(settings.SERVER_URL + '/updateAllProviderSchedules', {})
    result = response.get('result_code')
    if result == '0':
        return render(request, 'vacay/beauty_entry.html')
    else:return redirect('/home', {'error':'true'})

def women_beauty(request):
    return render(request, 'vacay/female_beauty.html')

def men_beauty(request):
    return render(request, 'vacay/male_beauty.html')

def beauty(request):
    category = request.GET['category']
    request.session['beauty_category'] = category
    return render(request, 'vacay/beauty_location_select.html')

def b_loc(request):
    location = request.GET['location']
    request.session['beauty_location'] = location

    categoryList = ['whair', 'wblowout', 'wmanicure', 'wmassage', 'wwax', 'wfacial', 'wmakeover', 'mhaircut', 'mhotshave', 'mmanicure', 'mmassage', 'mwax', 'mfacial']
    locationList=  ['sanfran', 'newyork', 'chicago', 'denver', 'austin', 'london']

    categoryId = categoryList.index(request.session['beauty_category'])
    locationId = locationList.index(request.session['beauty_location'])

    categories = ['Hair(Women)', 'Blowout', 'Manicure/Pedicure(Women)', 'Massage(Women)', 'Wax(Women)', 'Facial(Women)', 'Makeover',
                  'Hair(Men)', 'Hot Shave', 'Manicure/Pedicure(Men)', 'Massage(Men)', 'Wax(Men)', 'Facial(Men)']
    locations = ['San Francisco', 'New York', 'Chicago', 'Denver', 'Austin', 'London']

    data = {
        'proBeautyCategory':categories[categoryId],
        'proCity':locations[locationId]
    }
    serviceList = []
    response = get_info(settings.SERVER_URL + '/getServiceProviderInfo', data)
    result = response.get('result_code')
    if result == '0':
        beautyInfo = response.get('service_provider_info')
        # return HttpResponse(len(beautyInfo))
        if len(beautyInfo) >0:
            for info in beautyInfo:
                service = Service()
                service.serviceid = info['serviceid']
                service.proid = info['proid']
                service.proBeautyCategory = info['proBeautyCategory']
                service.proBeautySubCategory = info['proBeautySubcategory']
                service.proServicePrice = info['proServicePrice']
                service.proServicePictureUrl = info['proServicePictureUrl']
                service.proServiceDescription = info['proServiceDescription']
                service.providerPhotoUrl = info['proProfileImageUrl']
                service.providerFirstName = info['proFirstName']
                service.providerLastName = info['proLastName']
                service.providerEmail = info['proEmail']
                service.providerPhone = info['proPhone']
                service.providerCity = info['proCity']
                service.providerAddress = info['proAddress']
                service.providerCompany = info['proCompany']
                service.providerToken = info['proToken']
                service.providerAvailable = info['proAvailable']
                service.providerServicePercent = info['proServicePercent']
                service.providerSalary = info['proSalary']
                service.providerProductSalePercent = info['proProductSalePercent']

                serviceList.insert(0, service)

        category = request.session['beauty_category']
        if category == 'whair':
            return render(request, 'vacay/wmhair.html', {'services': serviceList})
        elif category == 'wblowout':
            return render(request, 'vacay/wmblowout.html', {'services': serviceList})
        elif category == 'wmanicure':
            return render(request, 'vacay/wmmanicure.html', {'services': serviceList})
        elif category == 'wmassage':
            return render(request, 'vacay/wmmassage.html', {'services': serviceList})
        elif category == 'wwax':
            return render(request, 'vacay/wmwax.html', {'services': serviceList})
        elif category == 'wfacial':
            return render(request, 'vacay/wmfacial.html', {'services': serviceList})
        elif category == 'wmakeover':
            return render(request, 'vacay/wmmakeover.html', {'services': serviceList})
        elif category == 'mhaircut':
            return render(request, 'vacay/mhaircut.html', {'services': serviceList})
        elif category == 'mhotshave':
            return render(request, 'vacay/mhotshave.html', {'services': serviceList})
        elif category == 'mmanicure':
            return render(request, 'vacay/mmanicure.html', {'services': serviceList})
        elif category == 'mmassage':
            return render(request, 'vacay/mmassage.html', {'services': serviceList})
        elif category == 'mwax':
            return render(request, 'vacay/mwax.html', {'services': serviceList})
        elif category == 'mfacial':
            return render(request, 'vacay/mfacial.html', {'services': serviceList})

    else:
        return redirect('/home', {'error': 'true'})


def service_detail(request, service_id):
    serviceList = []
    categoryList = ['whair', 'wblowout', 'wmanicure', 'wmassage', 'wwax', 'wfacial', 'wmakeover', 'mhaircut',
                    'mhotshave', 'mmanicure', 'mmassage', 'mwax', 'mfacial']
    locationList = ['sanfran', 'newyork', 'chicago', 'denver', 'austin', 'london']

    categoryId = categoryList.index(request.session['beauty_category'])
    locationId = locationList.index(request.session['beauty_location'])

    categories = ['Hair(Women)', 'Blowout', 'Manicure/Pedicure(Women)', 'Massage(Women)', 'Wax(Women)', 'Facial(Women)',
                  'Makeover',
                  'Hair(Men)', 'Hot Shave', 'Manicure/Pedicure(Men)', 'Massage(Men)', 'Wax(Men)', 'Facial(Men)']
    locations = ['San Francisco', 'New York', 'Chicago', 'Denver', 'Austin', 'London']

    data = {
        'proBeautyCategory': categories[categoryId],
        'proCity': locations[locationId]
    }
    response = get_info(settings.SERVER_URL + '/getServiceProviderInfo', data)
    result = response.get('result_code')
    # return HttpResponse(result)
    if result == '0':
        beautyInfo = response.get('service_provider_info')
        # return HttpResponse(len(beautyInfo))
        if len(beautyInfo) > 0:
            for info in beautyInfo:
                service = Service()
                service.serviceid = info['serviceid']
                service.proid = info['proid']
                service.proBeautyCategory = info['proBeautyCategory']
                service.proBeautySubCategory = info['proBeautySubcategory']
                service.proServicePrice = info['proServicePrice']
                service.proServicePictureUrl = info['proServicePictureUrl']
                service.proServiceDescription = info['proServiceDescription']
                service.providerPhotoUrl = info['proProfileImageUrl']
                service.providerFirstName = info['proFirstName']
                service.providerLastName = info['proLastName']
                service.providerEmail = info['proEmail']
                service.providerPhone = info['proPhone']
                service.providerCity = info['proCity']
                service.providerAddress = info['proAddress']
                service.providerCompany = info['proCompany']
                service.providerToken = info['proToken']
                service.providerAvailable = info['proAvailable']
                service.providerServicePercent = info['proServicePercent']
                service.providerSalary = info['proSalary']
                service.providerProductSalePercent = info['proProductSalePercent']
                serviceList.insert(0, service)
                if info['serviceid'] == service_id:
                    request.session['service_id'] = service_id
                    request.session['blocation'] = service.providerAddress
                    request.session['b_company'] = service.providerCompany
                    return render(request, 'vacay/beauty_detail.html', {'service':service})

        category = request.session['beauty_category']
        if category == 'whair':
            return render(request, 'vacay/wmhair.html', {'services': serviceList})
        elif category == 'wblowout':
            return render(request, 'vacay/wmblowout.html', {'services': serviceList})
        elif category == 'wmanicure':
            return render(request, 'vacay/wmmanicure.html', {'services': serviceList})
        elif category == 'wmassage':
            return render(request, 'vacay/wmmassage.html', {'services': serviceList})
        elif category == 'wwax':
            return render(request, 'vacay/wmwax.html', {'services': serviceList})
        elif category == 'wfacial':
            return render(request, 'vacay/wmfacial.html', {'services': serviceList})
        elif category == 'wmakeover':
            return render(request, 'vacay/wmmakeover.html', {'services': serviceList})
        elif category == 'mhaircut':
            return render(request, 'vacay/mhaircut.html', {'services': serviceList})
        elif category == 'mhotshave':
            return render(request, 'vacay/mhotshave.html', {'services': serviceList})
        elif category == 'mmanicure':
            return render(request, 'vacay/mmanicure.html', {'services': serviceList})
        elif category == 'mmassage':
            return render(request, 'vacay/mmassage.html', {'services': serviceList})
        elif category == 'mwax':
            return render(request, 'vacay/mwax.html', {'services': serviceList})
        elif category == 'mfacial':
            return render(request, 'vacay/mfacial.html', {'services': serviceList})

        else:return redirect('/home', {'error':'true'})
    else:return redirect('/home', {'error':'true'})

def brequest(request, service_id):
    request.session['service_id'] = service_id
    eml = ''
    employee = ''
    user = CommonUser()
    if request.session['em_email'] != '':
        eml = request.session['em_email']
        users = Employee.objects.filter(email=eml)
        nameStr = users[0].name.split()
        first_name = nameStr[0]
        try:
            last_name = nameStr[1]
        except:
            last_name = ''
        user.first_name = first_name
        user.last_name = last_name
        user.email = eml
        user.photo_url = users[0].image
        employee = 'true'
    elif request.session['fb_email'] != '':
        eml = request.session['fb_email']
        users = CommonUser.objects.filter(email=eml)
        user = users[0]
    serviceList = []
    categoryList = ['whair', 'wblowout', 'wmanicure', 'wmassage', 'wwax', 'wfacial', 'wmakeover', 'mhaircut',
                    'mhotshave', 'mmanicure', 'mmassage', 'mwax', 'mfacial']
    locationList = ['sanfran', 'newyork', 'chicago', 'denver', 'austin', 'london']

    categoryId = categoryList.index(request.session['beauty_category'])
    locationId = locationList.index(request.session['beauty_location'])

    categories = ['Hair(Women)', 'Blowout', 'Manicure/Pedicure(Women)', 'Massage(Women)', 'Wax(Women)', 'Facial(Women)',
                  'Makeover',
                  'Hair(Men)', 'Hot Shave', 'Manicure/Pedicure(Men)', 'Massage(Men)', 'Wax(Men)', 'Facial(Men)']
    locations = ['San Francisco', 'New York', 'Chicago', 'Denver', 'Austin', 'London']

    data = {
        'proBeautyCategory': categories[categoryId],
        'proCity': locations[locationId]
    }
    response = get_info(settings.SERVER_URL + '/getServiceProviderInfo', data)
    result = response.get('result_code')
    # return HttpResponse(result)
    if result == '0':
        beautyInfo = response.get('service_provider_info')
        # return HttpResponse(len(beautyInfo))
        if len(beautyInfo) > 0:
            for info in beautyInfo:
                service = Service()
                service.serviceid = info['serviceid']
                service.proid = info['proid']
                service.proBeautyCategory = info['proBeautyCategory']
                service.proBeautySubCategory = info['proBeautySubcategory']
                service.proServicePrice = info['proServicePrice']
                service.proServicePictureUrl = info['proServicePictureUrl']
                service.proServiceDescription = info['proServiceDescription']
                service.providerPhotoUrl = info['proProfileImageUrl']
                service.providerFirstName = info['proFirstName']
                service.providerLastName = info['proLastName']
                service.providerEmail = info['proEmail']
                service.providerPhone = info['proPhone']
                service.providerCity = info['proCity']
                service.providerAddress = info['proAddress']
                service.providerCompany = info['proCompany']
                service.providerToken = info['proToken']
                service.providerAvailable = info['proAvailable']
                service.providerServicePercent = info['proServicePercent']
                service.providerSalary = info['proSalary']
                service.providerProductSalePercent = info['proProductSalePercent']
                serviceList.insert(0, service)
                if info['serviceid'] == service_id:
                    request.session['service_id'] = service_id

                    request.session['price'] = service.proServicePrice
                    request.session['percent'] = service.providerServicePercent
                    request.session['provider_token'] = service.providerToken

                    request.session['blocation'] = service.providerAddress
                    request.session['b_company'] = service.providerCompany
                    productList = []
                    if products(service.proid) is not None:
                        productList = products(service.proid)

                    return render(request, 'vacay/beauty_request.html', {'service':service, 'products':productList, 'me':user, 'employee':employee})
            return redirect('/service_detail/' + service_id)

        else:return redirect('/home', {'error':'true'})
    else:return redirect('/home', {'error':'true'})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def filter_beauties(request):
    if request.method == 'POST':
        category = request.POST.get('category', None)
        serviceList = []
        categoryList = ['whair', 'wblowout', 'wmanicure', 'wmassage', 'wwax', 'wfacial', 'wmakeover', 'mhaircut',
                        'mhotshave', 'mmanicure', 'mmassage', 'mwax', 'mfacial']
        locationList = ['sanfran', 'newyork', 'chicago', 'denver', 'austin', 'london']

        categoryId = categoryList.index(request.session['beauty_category'])
        locationId = locationList.index(request.session['beauty_location'])

        categories = ['Hair(Women)', 'Blowout', 'Manicure/Pedicure(Women)', 'Massage(Women)', 'Wax(Women)',
                      'Facial(Women)',
                      'Makeover',
                      'Hair(Men)', 'Hot Shave', 'Manicure/Pedicure(Men)', 'Massage(Men)', 'Wax(Men)', 'Facial(Men)']
        locations = ['San Francisco', 'New York', 'Chicago', 'Denver', 'Austin', 'London']

        data = {
            'proBeautyCategory': categories[categoryId],
            'proCity': locations[locationId]
        }
        response = get_info(settings.SERVER_URL + '/getServiceProviderInfo', data)
        result = response.get('result_code')
        # return HttpResponse(result)
        if result == '0':
            beautyInfo = response.get('service_provider_info')
            # return HttpResponse(len(beautyInfo))
            if len(beautyInfo) > 0:
                for info in beautyInfo:
                    service = Service()
                    service.serviceid = info['serviceid']
                    service.proid = info['proid']
                    service.proBeautyCategory = info['proBeautyCategory']
                    service.proBeautySubCategory = info['proBeautySubcategory']
                    service.proServicePrice = info['proServicePrice']
                    service.proServicePictureUrl = info['proServicePictureUrl']
                    service.proServiceDescription = info['proServiceDescription']
                    service.providerPhotoUrl = info['proProfileImageUrl']
                    service.providerFirstName = info['proFirstName']
                    service.providerLastName = info['proLastName']
                    service.providerEmail = info['proEmail']
                    service.providerPhone = info['proPhone']
                    service.providerCity = info['proCity']
                    service.providerAddress = info['proAddress']
                    service.providerCompany = info['proCompany']
                    service.providerToken = info['proToken']
                    service.providerAvailable = info['proAvailable']
                    service.providerServicePercent = info['proServicePercent']
                    service.providerSalary = info['proSalary']
                    service.providerProductSalePercent = info['proProductSalePercent']

                    key = service.proBeautySubCategory

                    if category == 'wmhair':
                        haircut = request.POST.get('haircut', None)
                        color = request.POST.get('color', None)
                        brazilian = request.POST.get('brazilian', None)
                        keratin = request.POST.get('keratin', None)
                        deep = request.POST.get('deep', None)

                        if key == haircut or key == color or key == brazilian or key == keratin or key == deep:
                            serviceList.insert(0, service)
                    elif category == 'wmblowout':
                        blowout = request.POST.get('blowout', None)

                        if key == blowout:
                            serviceList.insert(0, service)
                    elif category == 'wmfacial':
                        basic = request.POST.get('basic', None)
                        premium = request.POST.get('premium', None)

                        if key == basic or key == premium:
                            serviceList.insert(0, service)
                    elif category == 'wmmakeover':
                        makeover = request.POST.get('makeover', None)

                        if key == makeover:
                            serviceList.insert(0, service)
                    elif category == 'wmmanicure':
                        manicure = request.POST.get('manicure', None)
                        mangel = request.POST.get('mangel', None)
                        pedicure = request.POST.get('pedicure', None)
                        pedgel = request.POST.get('pedgel', None)
                        pink = request.POST.get('pink', None)

                        if key == manicure or key == mangel or key == pedicure or key == pedgel or key == pink:
                            serviceList.insert(0, service)
                    elif category == 'wmmassage':
                        deep50 = request.POST.get('deep50', None)
                        deep90 = request.POST.get('deep90', None)
                        swedish50 = request.POST.get('swedish50', None)
                        swedish90 = request.POST.get('swedish90', None)

                        if key == deep50 or key == deep90 or key == swedish50 or key == swedish90:
                            serviceList.insert(0, service)
                    elif category == 'wmwax':
                        eye = request.POST.get('eye', None)
                        lip = request.POST.get('lip', None)
                        bikini = request.POST.get('bikini', None)
                        wbrazilian = request.POST.get('wbrazilian', None)

                        if key == eye or key == lip or key == bikini or key == wbrazilian:
                            serviceList.insert(0, service)
                    elif category == 'mhaircut':
                        classiccut = request.POST.get('classiccut', None)
                        frostycolor = request.POST.get('frostrycolor', None)
                        trendycut = request.POST.get('trendycut', None)
                        classiccolor = request.POST.get('classiccolor', None)

                        if key == classiccut or key == frostycolor or key == trendycut or key == classiccolor:
                            serviceList.insert(0, service)
                    elif category == 'mhotshave':
                        executive = request.POST.get('executive', None)
                        chairman = request.POST.get('chairman', None)
                        neck = request.POST.get('neck', None)
                        hot = request.POST.get('hot', None)

                        if key == executive or key == chairman or key == neck or key == hot:
                            serviceList.insert(0, service)
                    elif category == 'mmanicure':
                        manicure = request.POST.get('manicure', None)
                        heaven = request.POST.get('heaven', None)
                        feet = request.POST.get('feet', None)

                        if key == manicure or key == heaven or key == feet:
                       #     return HttpResponse(key)
                            serviceList.insert(0, service)
                    elif category == 'mmassage':
                        deep = request.POST.get('deep', None)
                        swedish = request.POST.get('swedish', None)
                        neckback = request.POST.get('neckback', None)
                        sugar = request.POST.get('sugar', None)

                        if key == deep or key == swedish or key == neckback or key == sugar:
                            serviceList.insert(0, service)
                    elif category == 'mwax':
                        chest = request.POST.get('chest', None)
                        nose = request.POST.get('nose', None)
                        back = request.POST.get('back', None)
                        eye = request.POST.get('eye', None)

                        if key == chest or key == nose or key == back or key == eye:
                            serviceList.insert(0, service)
                    elif category == 'mfacial':
                        rejuvenating = request.POST.get('rejuvenating', None)
                        fountain = request.POST.get('fountain', None)
                        destress = request.POST.get('destress', None)
                        gentleman = request.POST.get('gentleman', None)

                        if key == rejuvenating or key == fountain or key == destress or key == gentleman:
                            serviceList.insert(0, service)

            return render(request, 'vacay/beauty_list.html', {'services':serviceList})

        else:
            return redirect('/home', {'error':'true'})



def get_schedule(request, proid):
    scheduleList = []
    data = {'proid':proid}
    response = get_info(settings.SERVER_URL + '/getProviderAvailable', data)
    result = response.get('result_code')
    if result == '0':
        scheduleInfo = response.get('available_info')
        for info in scheduleInfo:
            schedule = ProviderSchedule()
            schedule.availableid = info['availableid']
            schedule.proid = info['proid']
            schedule.availableStart = info['availableStart']
            schedule.availableEnd = info['availableEnd']
            schedule.availableComment = info['availableComment']
            scheduleList.insert(0, schedule)
        return render(request, 'vacay/beauty_schedule.html', {'schedules':scheduleList})
    else:return redirect('/home', {'error':'true'})

def service_media(request, service_id):
    data = {
        'item_id': service_id,
        'item': 'service'
    }
    serviceMedia = get_info(settings.SERVER_URL + "/get_media", data)
    result = serviceMedia.get('result_code')
    if result == '0':
        media = serviceMedia.get('media')
        md = Media()
        md.video = media['video_url']
        md.youtube = media['youtube_url']
        md.imageA = media['image_a']
        md.imageB = media['image_b']
        md.imageC = media['image_c']
        md.imageD = media['image_d']
        md.imageE = media['image_e']
        md.imageF = media['image_f']

        return render(request, 'vacay/announce_media.html', {'media': md})
    else:
        return redirect('/service_detail/' + request.session['service_id'])

def products(proid):
    productList = []
    data = {'proid': proid}
    response = get_info(settings.SERVER_URL + '/getProductInfo', data)
    result = response.get('result_code')
    if result == '0':
        productInfo = response.get('productInfo')
        for info in productInfo:
            product = Product()
            product.itemid = info['itemid']
            product.brand = info['itemBrand']
            product.name = info['itemName']
            product.size = info['itemSize']
            product.product = info['itemProduct']
            product.price = info['itemPrice']
            product.description = info['itemDescription']
            product.pictureUrl = info['itemPictureUrl']
            product.inventoryNum = info['itemInventoryNum']
            product.saleStatus = info['itemSaleStatus']
            productList.insert(0, product)
        return productList
    else:
        return None

def get_products(request, proid):
    categoryList = ['whair', 'wblowout', 'wmanicure', 'wmassage', 'wwax', 'wfacial', 'wmakeover', 'mhaircut',
                    'mhotshave', 'mmanicure', 'mmassage', 'mwax', 'mfacial']
    locationList = ['sanfran', 'newyork', 'chicago', 'denver', 'austin', 'london']

    categoryId = categoryList.index(request.session['beauty_category'])
    locationId = locationList.index(request.session['beauty_location'])

    categories = ['Hair(Women)', 'Blowout', 'Manicure/Pedicure(Women)', 'Massage(Women)', 'Wax(Women)', 'Facial(Women)',
                  'Makeover',
                  'Hair(Men)', 'Hot Shave', 'Manicure/Pedicure(Men)', 'Massage(Men)', 'Wax(Men)', 'Facial(Men)']
    locations = ['San Francisco', 'New York', 'Chicago', 'Denver', 'Austin', 'London']
    data = {
        'proBeautyCategory': categories[categoryId],
        'proCity': locations[locationId]
    }
    response = get_info(settings.SERVER_URL + '/getServiceProviderInfo', data)
    result = response.get('result_code')
    # return HttpResponse(result)
    if result == '0':
        beautyInfo = response.get('service_provider_info')
        # return HttpResponse(len(beautyInfo))
        if len(beautyInfo) > 0:
            for info in beautyInfo:
                if proid == info['proid']:
                    request.session['percent'] = info['proProductSalePercent']
                    request.session['provider_token'] = info['proToken']
                    request.session['provider_email'] = info['proEmail']
                    break
    productList = []
    data = {'proid':proid}
    response = get_info(settings.SERVER_URL + '/getProductInfo', data)
    result = response.get('result_code')
    if result == '0':
        productInfo = response.get('productInfo')
        for info in productInfo:
            product = Product()
            product.itemid = info['itemid']
            product.brand = info['itemBrand']
            product.name = info['itemName']
            product.size = info['itemSize']
            product.product = info['itemProduct']
            product.price = info['itemPrice']
            product.description = info['itemDescription']
            product.pictureUrl = info['itemPictureUrl']
            product.inventoryNum = info['itemInventoryNum']
            product.saleStatus = info['itemSaleStatus']
            product.location = request.session['blocation']
            product.company = request.session['b_company']
            productList.insert(0, product)
        request.session['proid'] = proid
        return render(request, 'vacay/beauty_products.html', {'products':productList})
    else:
        return redirect('/home', {'error':'true'})

def product_detail(request, itemid):
    productList = []
    employee = ''
    data = {'proid': request.session['proid']}
    response = get_info(settings.SERVER_URL + '/getProductInfo', data)
    result = response.get('result_code')
    if result == '0':
        productInfo = response.get('productInfo')
        for info in productInfo:
            product = Product()
            product.itemid = info['itemid']
            product.brand = info['itemBrand']
            product.name = info['itemName']
            product.size = info['itemSize']
            product.product = info['itemProduct']
            product.price = info['itemPrice']
            product.description = info['itemDescription']
            product.pictureUrl = info['itemPictureUrl']
            product.inventoryNum = info['itemInventoryNum']
            product.saleStatus = info['itemSaleStatus']
            product.location = request.session['blocation']
            product.company = request.session['b_company']
            productList.insert(0, product)
            if info['itemid'] == itemid:
                request.session['itemid'] = itemid
                request.session['price'] = product.price
                if request.session['em_email'] != '':
                    employee = 'true'
                return render(request, 'vacay/beauty_product_detail.html', {'product':product, 'provider_email':request.session['provider_email'], 'employee': employee})

        return render(request, 'vacay/beauty_products.html', {'products': productList})
    else:
        return redirect('/home', {'error': 'true'})

def product_media(request, itemid):
    data = {
        'item_id': itemid,
        'item': 'product'
    }
    serviceMedia = get_info(settings.SERVER_URL + "/get_media", data)
    result = serviceMedia.get('result_code')
    if result == '0':
        media = serviceMedia.get('media')
        md = Media()
        md.video = media['video_url']
        md.youtube = media['youtube_url']
        md.imageA = media['image_a']
        md.imageB = media['image_b']
        md.imageC = media['image_c']
        md.imageD = media['image_d']
        md.imageE = media['image_e']
        md.imageF = media['image_f']

        return render(request, 'vacay/announce_media.html', {'media': md})
    else:
        return redirect('/product_detail/' + request.session['itemid'])

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def request_beauty(request):
    if request.method == 'POST':
        provider_email = request.POST.get('providerEmail', None)
        provider_name = request.POST.get('providerName', None)
        me_email = ''
        me_name = ''
        me_photo = ''
        if request.session['em_email'] != '':
            me_email = request.session['em_email']
            users = Employee.objects.filter(email=me_email)
            me = users[0]
            me_name = me.name
            me_photo = me.image
        elif request.session['fb_email'] != '':
            me_email = request.session['fb_email']
            users = CommonUser.objects.filter(email=me_email)
            me = users[0]
            me_name = me.first_name + ' ' + me.last_name
            me_photo = me.photo_url
        request_date = strftime("%Y-%m-%d %H:%M", gmtime())
        text = request.POST.get('text', None)
        lat = request.POST.get('lat', None)
        lng = request.POST.get('lng', None)
        moreloc = request.POST.get('moreloc', None)
        req_date = request.POST.get('datetime', None)
        location = request.POST.get('location', None)
        beautySubName = request.POST.get('beautySubName', None)
        beautyName = request.POST.get('beautyName', None)

        if req_date == '' or req_date == 'None':
            context = {'item': 'beautyrequest', 'response': 'Please input your request date & time for beauty service.'}
            return render(request, 'vacay/result.html', context)
        if location == '' or location == 'None':
            context = {'item': 'beautyrequest', 'response': 'Please input your request location for beauty service.'}
            return render(request, 'vacay/result.html', context)

        if moreloc == 'None': moreloc = ''

        message = 'Hi, '+provider_name+'\n'+me_name+' wants '+beautySubName+' as following:\n'+'Requested Date & Time:\n '+req_date+'\n'+'Requested Location:\n '
        message = message +location + '\n' + moreloc + '\n'+'Service Category: '+beautyName+'\n'+'Service Name: '+beautySubName+'\n'+'Description: '+text+'\n\n'
        message = message + 'Please review the information. If you have questions, you can reply directly to the customer. If you want to accept or decline, please click here.\n'
        message = message + 'Thanks\n'+request_date+'\n'+me_name

        msg = message

        if lat == 'None' or lat == '':
            lat = '0.0'
        if lng == 'None' or lng == '':
            lng = '0.0'
        dt = {
            'name': me_name,
            'photo_url': me_photo,
            'from_mail': me_email,
            'to_mail': provider_email,
            'request_date': request_date,
            'text_message': message,
            'service': beautySubName,
            'service_reqdate':req_date,
            'lon_message': lng,
            'lat_message': lat
        }
        response = post_info('http://18.216.124.61/makeMail', dt)
        result_code = response.get('result_code')
        # return HttpResponse(result_code)
        if result_code == '0':
            mail_id = response.get('mail_id')
            param = {
                'mail_id': mail_id
            }
            param2 = {
                'mail_id': mail_id,
                'message': message
            }
            try:
                photo = request.FILES['photo']

                files = {'file': photo}
                response2 = post_file('http://18.216.124.61/uploadMailPhoto', files, param)
                result_code = response2.get('result_code')

                response = post_info('http://18.216.124.61/sendMailMes', param2)
                result = response.get('result')
                context = {
                    'msg': msg,
                    'me_name': me_name,
                    'me_email': me_email,
                    'me_photo': me_photo,
                    'mail_id': mail_id,
                    'proemail': provider_email,
                    'service_name': beautySubName,
                    'service_reqdate': req_date,
                    'mail_result': result
                }
                return render(request, 'vacay/beauty_reqresult.html', context)

            except MultiValueDictKeyError or FileNotFoundError:
                print("File Not Exist")

            response = post_info('http://18.216.124.61/sendMailMes', param2)
            result = response.get('result')
            context = {
                'msg': msg,
                'me_name': me_name,
                'me_email': me_email,
                'me_photo': me_photo,
                'mail_id': mail_id,
                'proemail': provider_email,
                'service_name': beautySubName,
                'service_reqdate': req_date,
                'mail_result': result
            }
            return render(request, 'vacay/beauty_reqresult.html', context)
        else:
            context = {'item': 'beautyrequest', 'response': 'Error!'}
            return render(request, 'vacay/result.html', context)

def bucks(request):
    employees = Employee.objects.filter(email=request.session['em_email'])
    em_id = employees[0].em_id
    response = get_GET_info(settings.SERVER_URL + "/getVaCayBucksInfo", em_id)
    result = response.get('result_code')
    if result == '0':
        bucksInfo = response.get('bucks_data')
        name = bucksInfo[0]['em_name']
        photo = bucksInfo[0]['em_image']
        given_buck = bucksInfo[0]['em_givenbuck']
        used_buck = bucksInfo[0]['em_usedbuck']
        given_buck = given_buck.replace('$', '')
        used_buck = used_buck.replace('$', '')
        if given_buck == '' or given_buck == 'None':
            given_buck = '0'
        if used_buck == '' or used_buck == 'None':
            used_buck = '0'
        # return HttpResponse(given_buck+'/'+used_buck)
        given = float(given_buck)
        used = float(used_buck)
        rest = given - used
        restStr = '$' + str(rest)
        context = {
            'name': name,
            'photo': photo,
            'given_buck': '$'+given_buck,
            'used_buck': '$'+used_buck,
            'rest': restStr
        }
        return render(request, 'vacay/buck_status.html', context)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def updateBuck(request):
    if request.method == 'POST':
        newbuck = request.POST.get('newbuck', None)
        users = Employee.objects.filter(email=request.session['em_email'])
        em_id = users[0].em_id
        data = {
            'em_id': em_id,
            'amount': newbuck.replace('$', '')
        }
        response = post_info(settings.SERVER_URL + '/updateGivenBuck', data)
        result = response.get('result_code')
        if result == '0':
            context = {'item':'buckupdate', 'response':'Success!'}
        elif result == '99':
            context = {'item': 'buckupdate', 'response': 'Please enter amount more than old'}
        elif result == '100':
            context = {'item':'buckupdate', 'response':'Can\'t exceed limit'}
        else:
            context = {'item':'buckupdate', 'response':'Error!'}
        return render(request, 'vacay/result.html', context)

def check_payment(request):
    # return render(request, 'vacay/stripe_payment.html')
    proEmail = request.GET['proemail']
    request.session['provider_email'] = proEmail
    data = {'proEmail':proEmail}
    response = get_info(settings.SERVER_URL + '/getAdminPaymentAccountId', data)
    result = response.get('result_code')
    if result == '0':
        payment_id = response.get('accountid')
        if payment_id != '' and payment_id is not None:
            request.session['admin_token'] = payment_id
            if request.session['provider_token'] is not None and request.session['provider_token'] != '':
                price = float(request.session['price'].replace('$', '').replace(',', '')) * 100
                return render(request, 'vacay/stripe_payment.html', {'price': price})
            else:
                context = {'item': 'beautyrequest', 'response': 'Sorry, this provider\'s payment isn\'t verified.'}
                return render(request, 'vacay/result.html', context)
        else:
            context = {'item': 'beautyrequest', 'response': 'Sorry, this provider\'s payment isn\'t verified.'}
            return render(request, 'vacay/result.html', context)
    elif result == '100':
        context = {'item': 'beautyrequest', 'response': 'Unverified provider!'}
        return render(request, 'vacay/result.html', context)
    else:
        context = {'item': 'beautyrequest', 'response': 'Server error!'}
        return render(request, 'vacay/result.html', context)

import stripe

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def pay_to_provider(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    if request.method == "POST":

        token = request.POST.get('token', None)

        adminToken = request.session['admin_token']
        providerToken = request.session['provider_token']

        if adminToken is not None and adminToken != '':
            amount = request.session['price']
            amount = amount.replace('$', '').replace(',', '')
            amount = int(float(amount) * 100)

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token  # obtained with Stripe.js
            )
            if charge is not None:
                percent = request.session['percent']
                percent = percent.replace('%', '')
                providerOffer = int(amount * 0.8 * float(percent) * 0.01)
                transfer = stripe.Transfer.create(
                    amount=providerOffer,
                    currency="usd",
                    destination=providerToken
                )
                if transfer is not None:
                    providerOffer2 = int(amount * 0.8 * (100 - float(percent)) * 0.01)
                    transfer2 = stripe.Transfer.create(
                        amount=providerOffer2,
                        currency="usd",
                        destination=adminToken
                    )
                    if transfer2 is not None:
                        paid_money = request.session['price']
                        data = {}
                        if request.session['em_email'] != '':
                            data = {
                                'senderEmail': request.session['em_email'],
                                'receiverEmail': request.session['provider_email'],
                                'paidMoney': paid_money.replace('$', '').replace(',', '')
                            }
                        elif request.session['fb_email'] != '':
                            data = {
                                'senderEmail': request.session['fb_email'],
                                'receiverEmail': request.session['provider_email'],
                                'paidMoney': paid_money.replace('$', '').replace(',', '')
                            }
                        response = post_info(settings.SERVER_URL + '/savePaySendMail', data)
                        result = response.get('result')
                        if result == '0':
                            if request.session['em_email'] != '':
                                users = Employee.objects.filter(email=request.session['em_email'])
                                em_id = users[0].em_id
                                data = {
                                    'em_id': em_id,
                                    'amount': paid_money.replace('$', '').replace(',', '')
                                }
                                response = post_info(settings.SERVER_URL + '/addEmUsedBuck', data)

                            return render(request, 'vacay/stripe_payment.html', {'note': 'success'})
                        return render(request, 'vacay/stripe_payment.html', {'note': 'success'})
                    else:
                        return render(request, 'vacay/stripe_payment.html', {'transfer_error': 'failed'})
                else:
                    return render(request, 'vacay/stripe_payment.html', {'transfer_error': 'failed'})
            else:
                return render(request, 'vacay/stripe_payment.html', {'charge_error': 'failed'})
        else:
            return render(request, 'vacay/stripe_payment.html', {'seller_error': 'unverified'})

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def new_pay_to_provider(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    if request.method == "POST":

        token = request.POST.get('token', None)

        # return HttpResponse(token)
        adminToken = request.session['admin_token']
        providerToken = request.session['provider_token']

        if adminToken is not None and adminToken != '':
            amount = request.session['price']
            amount = amount.replace('$', '').replace(',', '')
            amount = int(float(amount) * 100)

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token  # obtained with Stripe.js
            )
            if charge is not None:
                percent = request.session['percent']
                percent = percent.replace('%', '')
                providerOffer = int(amount * 0.8 * float(percent) * 0.01)
                transfer = stripe.Transfer.create(
                    amount=providerOffer,
                    currency="usd",
                    destination=providerToken
                )
                if transfer is not None:
                    providerOffer2 = int(amount * 0.8 * (100 - float(percent)) * 0.01)
                    transfer2 = stripe.Transfer.create(
                        amount=providerOffer2,
                        currency="usd",
                        destination=adminToken
                    )
                    if transfer2 is not None:
                        paid_money = request.session['price']
                        data = {}
                        if request.session['em_email'] != '':
                            data = {
                                'senderEmail': request.session['em_email'],
                                'receiverEmail': request.session['provider_email'],
                                'paidMoney': paid_money.replace('$', '').replace(',', '')
                            }
                        elif request.session['fb_email'] != '':
                            data = {
                                'senderEmail': request.session['fb_email'],
                                'receiverEmail': request.session['provider_email'],
                                'paidMoney': paid_money.replace('$', '').replace(',', '')
                            }
                        response = post_info(settings.SERVER_URL + '/savePaySendMail', data)
                        result = response.get('result')
                        if result == '0':
                            if request.session['em_email'] != '':
                                users = Employee.objects.filter(email=request.session['em_email'])
                                em_id = users[0].em_id
                                data = {
                                    'em_id': em_id,
                                    'amount': paid_money.replace('$', '').replace(',', '')
                                }
                                response = post_info(settings.SERVER_URL + '/addEmUsedBuck', data)
                            return render(request, 'vacay/stripe_payment.html', {'note': 'success'})
                        return render(request, 'vacay/stripe_payment.html', {'note': 'success'})
                    else:
                        return render(request, 'vacay/stripe_payment.html', {'transfer_error': 'failed'})
                else:
                    return render(request, 'vacay/stripe_payment.html', {'transfer_error': 'failed'})
            else:
                return render(request, 'vacay/stripe_payment.html', {'charge_error': 'failed'})
        else:
            return render(request, 'vacay/stripe_payment.html', {'seller_error': 'unverified'})

    elif request.method == 'GET':
        pass


def inbox(request):
    eml = ''
    if request.session['fb_email'] != '':
        eml = request.session['fb_email']
    mails = MailBox.objects.filter(to_mail=eml).order_by('-id')
    return render(request, 'vacay/inbox.html', {'mails': mails})

def indetail(request, mail_id):
    eml = request.session['fb_email']
    users = Friend.objects.filter(email=eml)
    me = users[0]
    me_name = me.first_name + ' ' + me.last_name
    me_email = me.email
    me_photo = me.photo_url
    inbox = MailBox.objects.get(id=mail_id)
    return render(request, 'vacay/inbox_detail.html', {'mail':inbox, 'me_name':me_name, 'me_email': me_email, 'me_photo':me_photo})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def inloc(request):
    if request.method == 'POST':
        lat = request.POST.get('lat', None)
        lng = request.POST.get('lng', None)
        mail_id = request.POST.get('mail_id', None)
        # lat = '40.714224'
        # lng = '-73.961452'
        if lat != '' and lat != '0.0' and lng != '' and lng != '0.0':
            # return HttpResponse(lat)
            addr = decode_coordinates_to_address(lat, lng)
            return render(request, 'vacay/map_requested.html', {'lat':lat, 'lng':lng, 'address':addr})
        else:
            context = {'item': 'inloc', 'response': 'There is no any location requested from friend.'}
            return render(request, 'vacay/result.html', context)

def sentbox(request):
    mails = MailBox.objects.filter(from_mail=request.session['fb_email']).order_by('-id')
    return render(request, 'vacay/sentbox.html', {'mails': mails})

def sentdetail(request, mail_id):
    mail = MailBox.objects.get(id=mail_id)
    return render(request, 'vacay/sentdetail.html', {'mail': mail})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def sentloc(request):
    if request.method == 'POST':
        lat = request.POST.get('lat', None)
        lng = request.POST.get('lng', None)
        mail_id = request.POST.get('mail_id', None)
        # lat = '40.714224'
        # lng = '-73.961452'
        if lat != '' and lat != '0.0' and lng != '' and lng != '0.0':
            # return HttpResponse(lat)
            addr = decode_coordinates_to_address(lat, lng)
            return render(request, 'vacay/map_requested.html', {'lat':lat, 'lng':lng, 'address':addr})
        else:
            context = {'item': 'inloc', 'response': 'There is no any location requested to friend.'}
            return render(request, 'vacay/result.html', context)

def incompose(request):
    request.session['friend_email'] = ''
    request.session['friend_photo'] = ''
    return render(request, 'vacay/incompose.html')

def inreply(request, mail_id):
    mail = MailBox.objects.get(id=mail_id)

    request.session['friend_email'] = mail.from_mail
    request.session['friend_photo'] = mail.photo_url

    return render(request, 'vacay/incompose.html',
                              {'friend_email': request.session['friend_email'], 'friend_photo': request.session['friend_photo']})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def intofriend(request):
    if request.method == 'POST':
        friend_email = request.POST.get('email', None)
        friend_photo = request.POST.get('friend_photo', '')
        me_email = ''
        me_name = ''
        me_photo = ''
        em_id = ''
        if request.session['fb_email'] != '':
            me_email = request.session['fb_email']
            users = Friend.objects.filter(email=me_email)
            me = users[0]
            me_name = me.first_name + ' ' + me.last_name
            me_photo = me.photo_url
        request_date = str(int(round(time.time() * 1000)))
        subject = request.POST.get('subject', None)
        body = request.POST.get('body', None)
        lat = request.POST.get('lat', None)
        lng = request.POST.get('lng', None)
        message = subject+'\n'+body

        if lat == 'None' or lat == '':
            lat = '0.0'
        if lng == 'None' or lng == '':
            lng = '0.0'

        mail = MailBox()
        mail.from_mail = me_email
        mail.to_mail = friend_email
        mail.text_message = message
        mail.lon_message = lng
        mail.lat_message = lat
        mail.name = me_name
        mail.photo_url = me_photo
        mail.request_date = request_date

        mail.save()

        try:
            photo = request.FILES['photo']
            fs = FileSystemStorage()
            filename = fs.save(photo.name, photo)
            uploaded_file_url = fs.url(filename)

            mail.image_message_url = settings.URL + uploaded_file_url
            mail.save()

        except MultiValueDictKeyError or FileNotFoundError:
            print("File Not Exist")

        result = makemail(me_email, friend_email, message)

        friends = Friend.objects.filter(email=friend_email)
        if friends.count() > 0:
            friend = friends[0]
            friend_name = friend.first_name + ' ' + friend.last_name
            friend_photo = friend.photo_url

            createContFriend(me_email, friend_name, friend_email, friend_photo)

        return render(request, 'vacay/incompose.html',
                      {'friend_email': friend_email, 'friend_photo': friend_photo,
                       'success': 'true'})
    else:
        return redirect('/get_all_users')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def mapinattach(request):

    if request.method == 'POST':
        email = request.POST.get('email', None)
        subject = request.POST.get('subject', None)
        body = request.POST.get('body', None)

        if subject == 'None':
            subject = ''
        if body == 'None':
            body = ''

        context = {
            'email': email,
            'subject': subject,
            'body': body
        }
        return render(request, 'vacay/map_inattach.html', context)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def inattachloc(request):
    if request.method == 'POST':
        lat = request.POST.get('latitude', None)
        lng = request.POST.get('longitude', None)
        email = request.POST.get('email', None)
        subject = request.POST.get('subject', None)
        body = request.POST.get('body', None)

        friend_email = request.session['friend_email']
        friend_photo = request.session['friend_photo']

        context = {
            'friend_email':email,
            'friend_photo':friend_photo,
            'lat':lat,
            'lng':lng,
            'subject':subject,
            'body':body,
            'map': 'map'
        }
        return render(request, 'vacay/incompose.html', context)
    else:
        friend_email = request.session['friend_email']
        friend_photo = request.session['friend_photo']

        context = {
            'friend_email': friend_email,
            'friend_photo': friend_photo
        }
        if friend_email != '' and friend_photo != '':
            return render(request, 'vacay/incompose.html', context)
        else:
            return redirect('/inbox')

def infriends(request):
    userList = []
    users = Friend.objects.all().order_by('-id')
    if users.count() > 0:
        for user in users:
            if user.email != request.session['fb_email']:

                user.interests = "-" + user.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                                "\n-").replace(
                "\"", "").replace("[", "").replace("]", "")
                user.relationship = '-' + user.relationship.replace('common', '').replace('\n', '\n-')
                userList.append(user)

    contactors = ContFriend.objects.filter(user_email=request.session['fb_email'])
    return render(request, 'vacay/infriends.html', {'friends': userList, 'contactors': contactors})

def tobox(request, user_id):
    user = Friend.objects.get(id=user_id)
    request.session['friend_email'] = user.email
    request.session['friend_photo'] = user.photo_url
    return render(request, 'vacay/incompose.html',
                  {'friend_email': request.session['friend_email'], 'friend_photo': request.session['friend_photo']})

def inboxcontactor(request, contactor_id):
    contactor = ContFriend.objects.get(id=contactor_id)

    friend_email = contactor.email
    friend_name = contactor.name
    friend_photo = contactor.photo

    request.session['friend_email'] = friend_email
    request.session['friend_name'] = friend_name
    request.session['friend_photo'] = friend_photo
    if friend_email != '' and friend_photo != '':
        return render(request, 'vacay/incompose.html', {'friend_email': request.session['friend_email'],
                                                        'friend_photo': request.session['friend_photo']})
    else:
        return redirect('/infriends')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def accept(request):
    message = ''
    if request.method == 'POST':
        friend_email = request.POST.get('email', None)
        friend_name = request.POST.get('name', None)
        service = request.POST.get('service', None)
        service_reqdate = request.POST.get('service_reqdate', None)
        sts = request.POST.get('status', None)
        mailid = request.POST.get('mailid', None)
        me_name = ''
        me_photo = ''
        me_email = ''
        if request.session['em_email'] != '':
            users = Employee.objects.filter(email=request.session['em_email'])
            me = users[0]
            me_name = me.name
            me_photo = me.image
            me_email = me.email
        elif request.session['fb_email'] != '':
            users = CommonUser.objects.filter(email=request.session['fb_email'])
            me = users[0]
            me_name = me.first_name + ' ' + me.last_name
            me_photo = me.photo_url
            me_email = me.email
        elif request.session['pro_email'] != '':
            users = Provider.objects.filter(proEmail=request.session['pro_email'])
            me = users[0]
            me_name = me.proFirstName + ' ' + me.proLastName
            me_photo = me.proProfileImageUrl
            me_email = me.proEmail
        datetime = strftime("%Y-%m-%d %H:%M", gmtime())
        if sts == 'accepted':
            message = 'Hi, ' + friend_name + '\n' + me_name + ' has accepted you ' + service + ' with schedule of ' + service_reqdate + '\n' + 'Thanks\n' + datetime + '\n' + me_name
        elif sts == 'declined':
            message = 'Hi, ' + friend_name + '\n' + me_name + ' can\'t do you ' + service + ' with your requested schedule of ' + service_reqdate + '\n' + 'Please select another time or another service provider.\n' + 'We apologize for the inconvenience\n' + datetime + '\n' + me_name
        dt = {
            'name': me_name,
            'photo_url': me_photo,
            'from_mail': me_email,
            'to_mail': friend_email,
            'request_date': datetime,
            'text_message': message,
            'service': 'no_service',
            'service_reqdate': '',
            'lon_message': '0.0',
            'lat_message': '0.0'
        }
        response = post_info('http://18.216.124.61/makeMail', dt)
        result_code = response.get('result_code')
        if result_code == '0':
            mail_id = response.get('mail_id')
            param = {
                'mail_id': mail_id
            }
            param2 = {
                'mail_id': mailid,
                'status': sts
            }
            response = post_info('http://18.216.124.61/sendMailMessage', param)
            result = response.get('result')
            if result == '0':
                response = post_info(settings.SERVER_URL + '/update_request_message', param2)
                result = response.get('result_code')
                if result == '0':
                    return render(request, 'vacay/incompose.html', {'success': 'true'})
                else:
                    return render(request, 'vacay/incompose.html', {'failed': 'true'})
            else:
                return render(request, 'vacay/incompose.html', {'failed': 'true'})
        else:
            return render(request, 'vacay/incompose.html', {'failed': 'true'})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def acchat(request):
    message = ''
    if request.method == 'POST':
        friend_email = request.POST.get('email', None)
        friend_name = request.POST.get('name', None)
        service = request.POST.get('service', None)
        service_reqdate = request.POST.get('service_reqdate', None)
        sts = request.POST.get('status', None)
        mailid = request.POST.get('mailid', None)
        me_name = ''
        me_photo = ''
        me_email = ''
        if request.session['em_email'] != '':
            users = Employee.objects.filter(email=request.session['em_email'])
            me = users[0]
            me_name = me.name
            me_photo = me.image
            me_email = me.email
        elif request.session['fb_email'] != '':
            users = CommonUser.objects.filter(email=request.session['fb_email'])
            me = users[0]
            me_name = me.first_name + ' ' + me.last_name
            me_photo = me.photo_url
            me_email = me.email
        elif request.session['pro_email'] != '':
            users = Provider.objects.filter(proEmail=request.session['pro_email'])
            me = users[0]
            me_name = me.proFirstName + ' ' + me.proLastName
            me_photo = me.proProfileImageUrl
            me_email = me.proEmail
        datetime = strftime("%Y-%m-%d %H:%M", gmtime())
        if sts == 'accepted':
            message = 'Hi, ' + friend_name + '\n' + me_name + ' has accepted you ' + service + ' with schedule of ' + service_reqdate + '\n' + 'Thanks\n' + datetime + '\n' + me_name
        elif sts == 'declined':
            message = 'Hi, ' + friend_name + '\n' + me_name + ' can\'t do you ' + service + ' with your requested schedule of ' + service_reqdate + '\n' + 'Please select another time or another service provider.\n' + 'We apologize for the inconvenience\n' + datetime + '\n' + me_name
        dt = {
            'name': me_name,
            'photo_url': me_photo,
            'from_mail': me_email,
            'to_mail': friend_email,
            'request_date': datetime,
            'text_message': message,
            'service': 'no_service',
            'service_reqdate': '',
            'lon_message': '0.0',
            'lat_message': '0.0'
        }
        response = post_info('http://18.216.124.61/makeMail', dt)
        result_code = response.get('result_code')
        if result_code == '0':
            mail_id = response.get('mail_id')
            param = {
                'mail_id': mail_id
            }
            param2 = {
                'mail_id': mailid,
                'status': sts
            }
            response = post_info('http://18.216.124.61/sendMailMessage', param)
            result = response.get('result')
            if result == '0':
                response = post_info(settings.SERVER_URL + '/update_request_message', param2)
                result = response.get('result_code')
                if result == '0':
                    context = {'item': 'replaybooking',
                               'response': 'Your response sent!'}
                    return render(request, 'vacay/result.html', context)
                else:
                    context = {'item': 'replaybooking',
                               'response': 'Your response failed'}
                    return render(request, 'vacay/result.html', context)
            else:
                context = {'item': 'replaybooking',
                           'response': 'Your response failed'}
                return render(request, 'vacay/result.html', context)
        else:
            context = {'item': 'replaybooking',
                       'response': 'Your response failed'}
            return render(request, 'vacay/result.html', context)


def chatfriends(request):
    userList = []
    users = get_info(settings.SERVER_URL + "/getAllUsers", {})
    result_code = users['result_code']
    if result_code == '0':
        userInfo = users['user_infos']
        # user = userInfo[0]
        # text = "Hello World!"
        # text = text.replace(" ", "\r\n")
        # return HttpResponse(text)
        for user in userInfo:
            friend = CommonUser()
            friend.userid = user['userid']
            friend.first_name = user['first_name']
            friend.last_name = user['last_name']
            friend.email = user['email']
            friend.photo_url = user['photo_url']
            friend.age = user['age']
            friend.address = user['address']
            friend.job = user['job']
            friend.education = user['education']
            friend.survey = user['survey']
            friend.interests = "-"+user['interests'].replace("{","").replace("}","").replace("\",","\n-").replace("\"","").replace("[","").replace("]","")
            friend.relationship = user['relationship']
            friend.em_millennial = user['em_millennial']
            friend.place_name = user['place_name']
            friend.user_lat = user['user_lat']
            friend.user_lon = user['user_lon']

            if user['age'] != '0':
                if request.session['em_email'] != '':
                    if request.session['em_email'] == user['email']:
                        continue
                    if request.session['em_company'] == user['place_name']:
                        userList.insert(0, friend)
                elif request.session['fb_email'] != '':
                    if request.session['fb_email'] == user['email']:
                        continue
                    userList.insert(0, friend)
                elif request.session['pro_email'] != '':
                    if request.session['pro_email'] == user['email']:
                        continue
                    userList.insert(0, friend)
                elif request.session['manager_email'] != '':
                    if request.session['manager_email'] == user['email']:
                        continue
                    userList.insert(0, friend)
        contactors = []
        if request.session['em_email'] != '':
            contactors = Contactor.objects.filter(user_email=request.session['em_email'])
        elif request.session['fb_email'] != '':
            contactors = Contactor.objects.filter(user_email=request.session['fb_email'])
        elif request.session['pro_email'] != '':
            contactors = Contactor.objects.filter(user_email=request.session['pro_email'])
        elif request.session['manager_email'] != '':
            contactors = Contactor.objects.filter(user_email=request.session['manager_email'])

        return render(request, 'vacay/chatfriends.html', {'friends': userList, 'contactors':contactors})

    else:
        return redirect('/home')


def chatfriend(request):
    friend_email = request.GET['friend_email']
    if not '.com' in friend_email:
        friend_email = friend_email.replace('ddoott', '.') + '.com'
    request.session['mode'] = 'chat'
    users = get_info(settings.SERVER_URL + "/getUserProfile", {'email': friend_email})
    result_code = users['result_code']

    # return HttpResponse(result_code)

    if result_code == '0':
        userInfo = users['user_profile']
        friend = CommonUser()
        friend.first_name = userInfo[0]['first_name']
        friend.last_name = userInfo[0]['last_name']
        friend.email = userInfo[0]['email']
        friend.photo_url = userInfo[0]['photo_url']
        request.session['friend_email'] = friend.email
        request.session['friend_name'] = friend.first_name + ' ' + friend.last_name
        request.session['friend_photo'] = friend.photo_url
        if request.session['em_email'] != '':
            eml = request.session['em_email']
            users = get_info(settings.SERVER_URL + "/getUserProfile", {'email': eml})
            result_code = users['result_code']
            if result_code == '0':
                userInfo = users['user_profile']
                me = CommonUser()
                me.userid = userInfo[0]['userid']
                me.first_name = userInfo[0]['first_name']
                me.last_name = userInfo[0]['last_name']
                me.email = userInfo[0]['email']
                me.photo_url = userInfo[0]['photo_url']

                return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
        elif request.session['fb_email'] != '':
            eml = request.session['fb_email']
            users = get_info(settings.SERVER_URL + "/getUserProfile", {'email': eml})
            result_code = users['result_code']
            if result_code == '0':
                userInfo = users['user_profile']
                me = CommonUser()
                me.userid = userInfo[0]['userid']
                me.first_name = userInfo[0]['first_name']
                me.last_name = userInfo[0]['last_name']
                me.email = userInfo[0]['email']
                me.photo_url = userInfo[0]['photo_url']

                return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
        elif request.session['pro_email'] != '':
            users = Provider.objects.filter(proEmail=request.session['pro_email'])
            me = CommonUser()
            me.userid = users[0].proid
            me.first_name = users[0].proFirstName
            me.last_name = users[0].proLastName
            me.email = users[0].proEmail
            me.photo_url = users[0].proProfileImageUrl

            return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
        elif request.session['manager_email'] != '':
            users = AdminUser.objects.filter(adminEmail=request.session['manager_email'])
            me = CommonUser()
            me.userid = users[0].adminID
            name = users[0].adminName
            nameStr = name.split()
            first_name = nameStr[0]
            try:
                last_name = nameStr[1]
            except:
                last_name = ''
            me.first_name = first_name
            me.last_name = last_name
            me.email = users[0].adminEmail
            me.photo_url = users[0].adminImageUrl

            return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
        else:
            return redirect('/home', {'error': 'true'})

def vacay_job_detail(request, job_id):

    jobData = get_info(settings.SERVER_URL + "/get_all_jobs_for_sharing", {})
    result = jobData.get('result_code')
    if result == '0':
        jobInfo = jobData.get('job_info')
        for jobinfo in jobInfo:
            if job_id == jobinfo['job_id']:
                request.session['vacay_job_id'] = job_id
                job = Job()
                job.job_id = jobinfo['job_id']
                job.adminID = jobinfo['adminID']
                job.adminlogo = jobinfo['adminLogoImageUrl']
                job.req = jobinfo['job_req']
                job.title = jobinfo['job_name']
                job.department = jobinfo['job_department']
                job.location = jobinfo['job_location']
                job.description = jobinfo['job_description']
                job.postdate = jobinfo['job_postdate']
                job.empty = jobinfo['job_empty']
                job.admincompany = jobinfo['adminCompany']
                job.survey = jobinfo['job_survey']

                adminEmail = get_em_adminEmail(job.adminID)

                if job.survey.startswith("http") and "?usp=sf_link" in job.survey:
                    job.survey = job.survey.replace("?usp=sf_link", "?embedded=true")
                    return render(request, 'vacay/vacay_job.html',
                                  {'job': job, 'adminEmail': adminEmail, 'survey': 'true'})
                else:
                    return render(request, 'vacay/vacay_job.html', {'job': job, 'adminEmail': adminEmail})
    else:
        return HttpResponse('<h2>Server Error!</h2>')

def vacay_job_media(request, job_id):
    data = {
        'item_id':job_id,
        'item':'job'
    }
    jobMedia = get_info(settings.SERVER_URL + "/get_job_media", data)
    result = jobMedia.get('result_code')
    if result == '0':
        media = jobMedia.get('media')
        video = media['video_url']
        youtube = media['youtube_url']
        return render(request, 'vacay/vacay_job_media.html', {'video':video, 'youtube':youtube})
    else:
        return render(request, '/vacay_job_detail_' + request.session['vacay_job_id'])

def vacay_job_loc(request):
    address = request.GET['address']
    address = address.replace('+', ' ')
    return render(request, 'vacay/vacay_job_map.html', {'address': address})

def vacay_all_jobs(request):
    jobList = []
    jobData = get_info(settings.SERVER_URL + "/get_all_jobs_for_sharing", {})
    result = jobData.get('result_code')
    if result == '0':
        jobInfo = jobData.get('job_info')
        for jobinfo in jobInfo:
            request.session['vacay_job_id'] = jobinfo['job_id']
            job = Job()
            job.job_id = jobinfo['job_id']
            job.adminID = jobinfo['adminID']
            job.adminlogo = jobinfo['adminLogoImageUrl']
            job.req = jobinfo['job_req']
            job.title = jobinfo['job_name']
            job.department = jobinfo['job_department']
            job.location = jobinfo['job_location']
            job.description = jobinfo['job_description']
            job.postdate = jobinfo['job_postdate']
            job.empty = jobinfo['job_empty']
            job.admincompany = jobinfo['adminCompany']
            job.survey = jobinfo['job_survey']

            jobList.insert(0, job)

        return render(request, 'vacay/vacay_all_jobs.html', {'jobs': jobList})
    else:
        return HttpResponse('<h2>Server Error!</h2>')

def proservices(request):
  #  return HttpResponse(request.session['pro_id'])
    serviceList = []
    users = Provider.objects.filter(proid=request.session['pro_id'])
    me = users[0]
    data={
        'proid':request.session['pro_id']
    }
    response = get_info(settings.SERVER_URL + '/getServiceByProviderId', data)
    result = response.get('result_code')
    if result == '0':
        beautyInfo = response.get('service_info')
        # return HttpResponse(len(beautyInfo))
        for info in beautyInfo:
            service = Service()
            service.serviceid = info['serviceid']
            service.proid = info['proid']
            service.proBeautyCategory = info['proBeautyCategory']
            service.proBeautySubCategory = info['proBeautySubCategory']
            service.proServicePrice = info['proServicePrice']
            service.proServicePictureUrl = info['proServicePictureUrl']
            service.proServiceDescription = info['proServiceDescription']
            service.providerAddress = me.proAddress
            service.providerCompany = me.proCompany
            service.providerTakeHome = info['providerTakeHome']
            service.managerTakeHome = info['managerTakeHome']

            serviceList.insert(0, service)
        return render(request, 'vacay/provider_services.html', {'services':serviceList})

def proproducts(request):
  #  return HttpResponse(request.session['pro_id'])
    productList = []
    users = Provider.objects.filter(proid=request.session['pro_id'])
    me = users[0]
    data={
        'proid':request.session['pro_id']
    }
    response = get_info(settings.SERVER_URL + '/getProductInfo', data)
    result = response.get('result_code')
    if result == '0':
        beautyInfo = response.get('productInfo')
        # return HttpResponse(len(beautyInfo))
        for info in beautyInfo:
            product = Product()
            product.itemid = info['itemid']
            product.brand = info['itemBrand']
            product.product = info['itemProduct']
            product.name = info['itemName']
            product.size = info['itemSize']
            product.price = info['itemPrice']
            product.location = me.proAddress
            product.company = me.proCompany
            product.description = info['itemDescription']
            product.pictureUrl = info['itemPictureUrl']
            product.inventoryNum = info['itemInventoryNum']
            product.saleStatus = info['itemSaleStatus']
            product.providerTakeHome = info['providerTakeHome']
            product.managerTakeHome = info['managerTakeHome']

            productList.insert(0, product)
        return render(request, 'vacay/provider_products.html', {'products':productList})

def proprodetail(request, itemid):
    productList = []
    users = Provider.objects.filter(proid=request.session['pro_id'])
    me = users[0]
    data = {'proid': request.session['pro_id']}
    response = get_info(settings.SERVER_URL + '/getProductInfo', data)
    result = response.get('result_code')
    if result == '0':
        productInfo = response.get('productInfo')
        for info in productInfo:
            product = Product()
            product.itemid = info['itemid']
            product.brand = info['itemBrand']
            product.name = info['itemName']
            product.size = info['itemSize']
            product.product = info['itemProduct']
            product.price = info['itemPrice']
            product.description = info['itemDescription']
            product.pictureUrl = info['itemPictureUrl']
            product.inventoryNum = info['itemInventoryNum']
            product.saleStatus = info['itemSaleStatus']
            product.location = me.proAddress
            product.company = me.proCompany
            product.providerTakeHome = info['providerTakeHome']
            product.managerTakeHome = info['managerTakeHome']

            if info['itemid'] == itemid:
                return render(request, 'vacay/provider_product_detail.html', {'product':product})

        return redirect('/proproducts')
    else:
        return redirect('/home', {'error': 'true'})

def procalendar(request):
    scheduleList = []
    proid = request.session['pro_id']
    data = {'proid': proid}
    response = get_info(settings.SERVER_URL + '/getProviderAvailable', data)
    result = response.get('result_code')
    if result == '0':
        scheduleInfo = response.get('available_info')
        for info in scheduleInfo:
            schedule = ProviderSchedule()
            schedule.availableid = info['availableid']
            schedule.proid = info['proid']
            schedule.availableStart = info['availableStart']
            schedule.availableEnd = info['availableEnd']
            schedule.availableComment = info['availableComment']
            scheduleList.insert(0, schedule)
        return render(request, 'vacay/provider_calendar.html', {'schedules': scheduleList})
    else:
        return redirect('/home', {'error': 'true'})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def upload_provider_schedule(request):
    if request.method == 'POST':
        data = request.POST.get('data', None)
        param = {
            'proid':request.session['pro_id'],
            'schedulestr':data
        }
        response = post_info(settings.SERVER_URL + '/uploadMultipleSchedule', param)
        result = response.get('result_code')
  #      return HttpResponse(data)
        if result == '0':
            scheduleList = []
            proid = request.session['pro_id']
            data = {'proid': proid}
            response = get_info(settings.SERVER_URL + '/getProviderAvailable', data)
            result = response.get('result_code')
            if result == '0':
                scheduleInfo = response.get('available_info')
                for info in scheduleInfo:
                    schedule = ProviderSchedule()
                    schedule.availableid = info['availableid']
                    schedule.proid = info['proid']
                    schedule.availableStart = info['availableStart']
                    schedule.availableEnd = info['availableEnd']
                    schedule.availableComment = info['availableComment']
                    scheduleList.insert(0, schedule)
                return render(request, 'vacay/provider_calendar.html', {'schedules': scheduleList, 'success':'true'})
            else:
                context = {'item': 'schedulepost',
                           'response': 'Server error!'}
                return render(request, 'vacay/result.html', context)
        else:
            scheduleList = []
            proid = request.session['pro_id']
            data = {'proid': proid}
            response = get_info(settings.SERVER_URL + '/getProviderAvailable', data)
            result = response.get('result_code')
            if result == '0':
                scheduleInfo = response.get('available_info')
                for info in scheduleInfo:
                    schedule = ProviderSchedule()
                    schedule.availableid = info['availableid']
                    schedule.proid = info['proid']
                    schedule.availableStart = info['availableStart']
                    schedule.availableEnd = info['availableEnd']
                    schedule.availableComment = info['availableComment']
                    scheduleList.insert(0, schedule)
                return render(request, 'vacay/provider_calendar.html', {'schedules': scheduleList, 'error': 'true'})
            else:
                context = {'item': 'schedulepost',
                           'response': 'Server error!'}
                return render(request, 'vacay/result.html', context)

def deleteschedule(request, availableid):
    param = {'availableid':availableid}
    response = post_info(settings.SERVER_URL + '/deleteProviderAvailable', param)
    result = response.get('result_code')
    if result == '0':
        return redirect('/procalendar')
    else:
        context = {'item': 'schedulepost',
                   'response': 'Server error!'}
        return render(request, 'vacay/result.html', context)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def search_vacayjobs(request):
    if request.method == 'POST':
        q = request.POST.get('q', None)
        jobList = []
        jobData = get_info(settings.SERVER_URL + "/get_all_jobs_for_sharing", {})
        result = jobData.get('result_code')
        if result == '0':
            jobInfo = jobData.get('job_info')
            for jobinfo in jobInfo:
                request.session['vacay_job_id'] = jobinfo['job_id']
                job = Job()
                job.job_id = jobinfo['job_id']
                job.adminID = jobinfo['adminID']
                job.adminlogo = jobinfo['adminLogoImageUrl']
                job.req = jobinfo['job_req']
                job.title = jobinfo['job_name']
                job.department = jobinfo['job_department']
                job.location = jobinfo['job_location']
                job.description = jobinfo['job_description']
                job.postdate = jobinfo['job_postdate']
                job.empty = jobinfo['job_empty']
                job.admincompany = jobinfo['adminCompany']
                job.survey = jobinfo['job_survey']
                if q.lower() in job.title.lower():
                    jobList.insert(0, job)
                elif q.lower() in job.department.lower():
                    jobList.insert(0, job)
                elif q.lower() in job.location.lower():
                    jobList.insert(0, job)
                elif q.lower() in job.description.lower():
                    jobList.insert(0, job)
                elif q.lower() in job.postdate.lower():
                    jobList.insert(0, job)
                elif q.lower() in job.empty.lower():
                    jobList.insert(0, job)
                elif q.lower() in job.admincompany.lower():
                    jobList.insert(0, job)
                elif q.lower() in job.req.lower():
                    jobList.insert(0, job)
            return render(request, 'vacay/vacay_all_jobs.html', {'jobs': jobList})
        else:
            return HttpResponse('<h2>Server Error!</h2>')

def proaccept(request, mailid):
    mails = get_info(settings.SERVER_URL + "/allmailsforserviceprovideracceptordecline", {})
    result_code = mails['result_code']
    # return HttpResponse(result_code)
    if result_code == '0':
        mailInfo = mails['maildata']
        for mail in mailInfo:
            if mail['mail_id'] == mailid:
                inbox = MailBox()
                inbox.mail_id = mail['mail_id']
                inbox.from_mail = mail['from_mail']
                inbox.to_mail = mail['to_mail']
                inbox.name = mail['name']
                inbox.photo_url = mail['photo_url']
                inbox.text_message = mail['text_message']
                inbox.request_date = mail['request_date']
                inbox.service = mail['service']
                inbox.service_reqdate = mail['service_reqdate']
                inbox.image_message_url = mail['image_message_url']
                inbox.lat_message = mail['lat_message']
                inbox.lon_message = mail['lon_message']

                datetime = strftime("%Y-%m-%d %H:%M", gmtime())

                friend_name = inbox.name
                friend_email = inbox.from_mail
                me_email = inbox.to_mail
                data = {'proEmail': me_email}
                proData = get_info(settings.SERVER_URL + "/getProviderByProEmail", data)
                result = proData.get('result_code')
                if result == '0':
                    data = proData.get('provider_info')
                    me_name = data[0]['proFirstName'] + ' ' + data[0]['proLastName']
                    me_photo = data[0]['proProfileImageUrl']

                    message = 'Hi, ' + friend_name + '\n' + me_name + ' has accepted you ' + inbox.service + ' with schedule of ' + inbox.service_reqdate + '\n' + 'Thanks\n' + datetime + '\n' + me_name
                    dt = {
                        'name': me_name,
                        'photo_url': me_photo,
                        'from_mail': me_email,
                        'to_mail': friend_email,
                        'request_date': datetime,
                        'text_message': message,
                        'service': 'no_service',
                        'service_reqdate': '',
                        'lon_message': '0.0',
                        'lat_message': '0.0'
                    }
                    response = post_info('http://18.216.124.61/makeMail', dt)
                    result_code = response.get('result_code')
                    if result_code == '0':
                        mail_id = response.get('mail_id')
                        param = {
                            'mail_id': mail_id
                        }
                        param2 = {
                            'mail_id': mailid,
                            'status': 'accepted'
                        }
                        response = post_info('http://18.216.124.61/sendMailMessage', param)
                        result = response.get('result')
                        if result == '0':
                            response = post_info(settings.SERVER_URL + '/update_request_message', param2)
                            result = response.get('result_code')
                            if result == '0':
                                context = {
                                    'message': message,
                                    'sender_name': me_name,
                                    'sender_email': me_email,
                                    'sender_photo': me_photo,
                                    'friend_email': friend_email
                                }
                                return render(request, 'vacay/sendreplynotifrommail.html', context)
                    else:
                        return HttpResponse('<h2>Server failed</h2>')
                else:
                    return HttpResponse('<h2>Server failed</h2>')
    else:
        return HttpResponse('<h2>Server failed</h2>')

def prodecline(request, mailid):
    mails = get_info(settings.SERVER_URL + "/allmailsforserviceprovideracceptordecline", {})
    result_code = mails['result_code']
    # return HttpResponse(result_code)
    if result_code == '0':
        mailInfo = mails['maildata']
        for mail in mailInfo:
            if mail['mail_id'] == mailid:
                inbox = MailBox()
                inbox.mail_id = mail['mail_id']
                inbox.from_mail = mail['from_mail']
                inbox.to_mail = mail['to_mail']
                inbox.name = mail['name']
                inbox.photo_url = mail['photo_url']
                inbox.text_message = mail['text_message']
                inbox.request_date = mail['request_date']
                inbox.service = mail['service']
                inbox.service_reqdate = mail['service_reqdate']
                inbox.image_message_url = mail['image_message_url']
                inbox.lat_message = mail['lat_message']
                inbox.lon_message = mail['lon_message']

                datetime = strftime("%Y-%m-%d %H:%M", gmtime())

                friend_name = inbox.name
                friend_email = inbox.from_mail
                me_email = inbox.to_mail
                data = {'proEmail': me_email}
                proData = get_info(settings.SERVER_URL + "/getProviderByProEmail", data)
                result = proData.get('result_code')
                if result == '0':
                    data = proData.get('provider_info')
                    me_name = data[0]['proFirstName'] + ' ' + data[0]['proLastName']
                    me_photo = data[0]['proProfileImageUrl']

                    message = 'Hi, ' + friend_name + '\n' + me_name + ' can\'t do you ' + inbox.service + ' with your requested schedule of ' + inbox.service_reqdate + '\n' + \
                              'Please select another time or another service provider.\n' + 'We apologize for the inconvenience\n' + datetime + '\n' + me_name
                    dt = {
                        'name': me_name,
                        'photo_url': me_photo,
                        'from_mail': me_email,
                        'to_mail': friend_email,
                        'request_date': datetime,
                        'text_message': message,
                        'service': 'no_service',
                        'service_reqdate': '',
                        'lon_message': '0.0',
                        'lat_message': '0.0'
                    }
                    response = post_info('http://18.216.124.61/makeMail', dt)
                    result_code = response.get('result_code')
                    if result_code == '0':
                        mail_id = response.get('mail_id')
                        param = {
                            'mail_id': mail_id
                        }
                        param2 = {
                            'mail_id': mailid,
                            'status': 'declined'
                        }
                        response = post_info('http://18.216.124.61/sendMailMessage', param)
                        result = response.get('result')
                        if result == '0':
                            response = post_info(settings.SERVER_URL + '/update_request_message', param2)
                            result = response.get('result_code')
                            if result == '0':
                                context = {
                                    'message': message,
                                    'sender_name': me_name,
                                    'sender_email': me_email,
                                    'sender_photo': me_photo,
                                    'friend_email': friend_email
                                }
                                return render(request, 'vacay/sendreplynotifrommail.html', context)
                    else:
                        return HttpResponse('<h2>Server failed</h2>')
                else:
                    return HttpResponse('<h2>Server failed</h2>')
    else:
        return HttpResponse('<h2>Server failed</h2>')

def manager_register(request):
    type = request.session['manager']
    return render(request, 'vacay/manager_register.html', {'type': type})


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def register_manager(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        company = ''
        try:
            company = request.POST.get('company', None)
        except MultiValueDictKeyError:
            print('No value exists')
        retail = '0'
        type = request.session['manager']
        if type == 'beauty':
            retail = '0'
        elif type == 'retail':
            retail = '1'
        elif type == 'company':
            retail = '2'
        if type == 'company':
            param = {
                'adminName': name,
                'adminEmail': email,
                'adminPassword': password,
                'adminCompany': company,
                'adminBroadmoor': retail
            }
            response = post_info(settings.SERVER_URL + '/registerEmployer', param)
            result = response.get('result_code')
            #      return HttpResponse(result)
            if result == '0':
                adminid = response.get('adminID')
                try:
                    photo = request.FILES['photo']
                    param2 = {
                        'adminID': adminid
                    }
                    files = {'file': photo}
                    response = post_file(settings.SERVER_URL + '/uploadAdminImage', files, param2)
                    result = response.get('result_code')
                    if result == '0':
                        try:
                            logo = request.FILES['logo']
                            files = {'file': logo}
                            response = post_file(settings.SERVER_URL + '/uploadAdminLogoImage', files, param2)
                            result = response.get('result_code')
                        except MultiValueDictKeyError or FileNotFoundError:
                            print('File doesn\'t exist')
                        request.session['manager_email'] = email
                        request.session['manager_id'] = adminid
                        if type == 'beauty':
                            return render(request, 'vacay/beautymanager_home.html')
                        elif type == 'retail':
                            return render(request, 'vacay/retailmanager_home.html')
                        elif type == 'company':
                            return render(request, 'vacay/companymanager_home.html')
                    else:
                        return render(request, 'vacay/manager_register.html', {'type': type, 'error': 'true'})
                except MultiValueDictKeyError or FileNotFoundError:
                    print('File doesn\'t exist')
                    photo = request.POST.get('b64')
                    #    return HttpResponse(photo)
                    param2 = {
                        'adminID': adminid,
                        'b64': photo
                    }
                    response = post_info(settings.SERVER_URL + '/uploadadminpicture', param2)
                    result = response.get('result_code')
                    if result == '0':
                        try:
                            logo = request.FILES['logo']
                            files = {'file': logo}
                            response = post_file(settings.SERVER_URL + '/uploadAdminLogoImage', files,
                                                 {'adminID': adminid})
                            result = response.get('result_code')
                        except MultiValueDictKeyError or FileNotFoundError:
                            print('File doesn\'t exist')
                        request.session['manager_email'] = email
                        request.session['manager_id'] = adminid
                        return redirect('/managerhome')
                    else:
                        return render(request, 'vacay/manager_register.html', {'type': type, 'error': 'true'})
            elif result == '101':
                return render(request, 'vacay/manager_register.html', {'type': type, 'exist': 'true'})
        else:
            param = {
                'adminName': name,
                'adminEmail': email,
                'adminPassword': password,
                'adminCompany': '',
                'adminBroadmoor': retail
            }
            response = post_info(settings.SERVER_URL + '/registerAdmin', param)
            result = response.get('result_code')
            #      return HttpResponse(result)
            if result == '0':
                adminid = response.get('adminID')
                try:
                    photo = request.FILES['photo']
                    param2 = {
                        'adminID': adminid
                    }
                    files = {'file': photo}
                    response = post_file(settings.SERVER_URL + '/uploadAdminImage', files, param2)
                    result = response.get('result_code')
                    if result == '0':
                        try:
                            logo = request.FILES['logo']
                            files = {'file': logo}
                            response = post_file(settings.SERVER_URL + '/uploadAdminLogoImage', files, param2)
                            result = response.get('result_code')
                        except MultiValueDictKeyError or FileNotFoundError:
                            print('File doesn\'t exist')
                        request.session['manager_email'] = email
                        request.session['manager_id'] = adminid
                        if type == 'beauty':
                            return render(request, 'vacay/beautymanager_home.html')
                        elif type == 'retail':
                            return render(request, 'vacay/retailmanager_home.html')
                        elif type == 'company':
                            return render(request, 'vacay/companymanager_home.html')
                    else:
                        return render(request, 'vacay/manager_register.html', {'type': type, 'error': 'true'})
                except MultiValueDictKeyError or FileNotFoundError:
                    print('File doesn\'t exist')
                    photo = request.POST.get('b64')
                    #    return HttpResponse(photo)
                    param2 = {
                        'adminID': adminid,
                        'b64': photo
                    }
                    response = post_info(settings.SERVER_URL + '/uploadadminpicture', param2)
                    result = response.get('result_code')
                    if result == '0':
                        try:
                            logo = request.FILES['logo']
                            files = {'file': logo}
                            response = post_file(settings.SERVER_URL + '/uploadAdminLogoImage', files,
                                                 {'adminID': adminid})
                            result = response.get('result_code')
                        except MultiValueDictKeyError or FileNotFoundError:
                            print('File doesn\'t exist')
                        request.session['manager_email'] = email
                        request.session['manager_id'] = adminid
                        return redirect('/managerhome')
                    else:
                        return render(request, 'vacay/manager_register.html', {'type': type, 'error': 'true'})
            elif result == '101':
                return render(request, 'vacay/manager_register.html', {'type': type, 'exist': 'true'})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def manager_login(request):
    if request.method == 'GET':
        type = request.GET['type']
        request.session['manager'] = type
        return render(request, 'vacay/manager_login.html')

def managerlogin(request):
    return render(request, 'vacay/manager_login.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def login_manager(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        param = {
            'adminEmail': email,
            'adminPassword': password
        }
        response = post_info(settings.SERVER_URL + '/loginAdmin', param)
        result = response.get('result_code')
   #     return HttpResponse(result)
        if result == '0':
            adminInfo = response.get('adminData')
            adminID = adminInfo[0]['adminID']
            adminEmail = adminInfo[0]['adminEmail']
            adminPassword = adminInfo[0]['adminPassword']
            adminBroadmoor = adminInfo[0]['adminBroadmoor']
            adminCompany = adminInfo[0]['adminCompany']
            adminLogo = adminInfo[0]['adminLogoImageUrl']
            adminImage = adminInfo[0]['adminImageUrl']
            adminName = adminInfo[0]['adminName']
            users = AdminUser.objects.filter(adminID=adminID)
            if users.count() == 0:
                adminUser = AdminUser()
                adminUser.adminID = adminID
                adminUser.adminEmail = adminEmail
                adminUser.adminPassword = adminPassword
                adminUser.adminBroadmoor = adminBroadmoor
                adminUser.adminCompany = adminCompany
                adminUser.adminLogoImageUrl = adminLogo
                adminUser.adminImageUrl = adminImage
                adminUser.adminName = adminName
                adminUser.save()
            request.session['manager_id'] = adminID
            request.session['manager_email'] = adminEmail

            users = AdminUser.objects.filter(adminID=adminID)
            me = users[0]

            request.session['em_email'] = ''
            request.session['em_adminID'] = ''
            request.session['pro_email'] = ''
            request.session['fb_email'] = ''

            type = request.session['manager']
            if type == 'beauty':
                return render(request, 'vacay/beautymanager_home.html', {'me':me})
            elif type == 'retail':
                return render(request, 'vacay/retailmanager_home.html', {'me':me})
            elif type == 'company':
                return render(request, 'vacay/companymanager_home.html', {'me':me})
        elif result == '113':
            return render(request, 'vacay/manager_login.html', {'note': 'true'})
        else:
            return render(request, 'vacay/manager_login.html', {'error': 'true'})
    elif request.method == 'GET':
        return render(request, 'vacay/manager_login.html', {'error': 'true'})

def manager_home(request):
    request.session['em_email'] = ''
    request.session['em_adminID'] = ''
    request.session['pro_email'] = ''
    request.session['fb_email'] = ''
    type = request.session['manager']
    adminid = request.session['manager_id']
    response = get_GET_info(settings.SERVER_URL + '/getAdminData', adminid)
    result = response.get('result_code')
    if result == '0':
        adminInfo = response.get('adminData')
        adminUser = AdminUser()
        adminUser.adminID = adminInfo[0]['adminID']
        adminUser.adminEmail = adminInfo[0]['adminEmail']
        adminUser.adminPassword = adminInfo[0]['adminPassword']
        adminUser.adminBroadmoor = adminInfo[0]['adminBroadmoor']
        adminUser.adminCompany = adminInfo[0]['adminCompany']
        adminUser.adminLogoImageUrl = adminInfo[0]['adminLogoImageUrl']
        adminUser.adminImageUrl = adminInfo[0]['adminImageUrl']
        adminUser.adminName = adminInfo[0]['adminName']
        if type == 'beauty':
            return render(request, 'vacay/beautymanager_home.html', {'me': adminUser})
        elif type == 'retail':
            return render(request, 'vacay/retailmanager_home.html', {'me': adminUser})
        elif type == 'company':
            return render(request, 'vacay/companymanager_home.html', {'me': adminUser})

def service_providers(request):
    providerList = []
    adminid = request.session['manager_id']
    response = post_info(settings.SERVER_URL + '/getProviderByAdminID', {'adminID': adminid})
    result = response.get('result_code')
    if result == '0':
        providerInfo = response.get('provider_info')
        for info in providerInfo:
            provider = Provider()
            provider.proid = info['proid']
            provider.proFirstName = info['proFirstName']
            provider.proLastName = info['proLastName']
            provider.proEmail = info['proEmail']
            provider.proProfileImageUrl = info['proProfileImageUrl']
            provider.proToken = info['proToken']

            providerList.insert(0, provider)
        return render(request, 'vacay/service_providers.html', {'providers':providerList})
    else:
        return redirect('/home')


def verify_account(request, proid):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    adminid = request.session['manager_id']
    response = post_info(settings.SERVER_URL + '/getProviderByAdminID', {'adminID': adminid})
    result = response.get('result_code')
    if result == '0':
        providerInfo = response.get('provider_info')
        for info in providerInfo:
            if info['proid'] == proid:
                provider = Provider()
                provider.proid = info['proid']
                provider.proFirstName = info['proFirstName']
                provider.proLastName = info['proLastName']
                provider.proEmail = info['proEmail']
                provider.proProfileImageUrl = info['proProfileImageUrl']
                provider.proToken = info['proToken']
                aid = provider.proToken
                if aid is not None and aid != '':
                    return redirect('/serviceproviders')
                else:
                    response = post_info(settings.SERVER_URL + '/account_details', {'email':provider.proEmail})
                    result = response.get('status')
                    if result == 'success':
                        accountInfo = response.get('account_data')
                        sts = accountInfo['status']
                        accountid = accountInfo['accountid']
                        if sts.startswith('Pending'):
                            return render(request, 'vacay/stripe_account.html',
                                          {'acc_id': accountid, 'provider': provider, 'pending':'true'})
                        else:
                            return redirect('/serviceproviders')
                    elif result == 'error':
                        account = stripe.Account.create(
                            type="custom",
                            country="US",
                            email=provider.proEmail
                        )
                        account_id = account['id']
                        param = {
                            'stripe_id': account_id,
                            'email': provider.proEmail,
                            'country': 'US'
                        }
                        response = post_info(settings.SERVER_URL + '/account_create', param)
                        result = response.get('result')
                        if result == 'success':
                            return render(request, 'vacay/stripe_account.html',
                                      {'acc_id': account_id, 'provider': provider, 'created':'true'})
                        else:
                            return HttpResponse('Payment account creation failed...')
        return redirect('/serviceproviders')
    else:
        return redirect('/serviceproviders')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def complete_account(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    if request.method == 'POST':
        proemail = request.POST.get('proemail', None)
        proname = request.POST.get('proname', None)

        acc_id = request.POST.get('acc_id', None)
        acc_number = request.POST.get('bank_number', None)
        country = request.POST.get('country', None)
        routing_number = request.POST.get('routing_number', None)
        day = request.POST.get('day', None)
        month = request.POST.get('month', None)
        year = request.POST.get('year', None)
        city = request.POST.get('city', None)
        address = request.POST.get('address', None)
        postal_code = request.POST.get('postal', None)
        state = request.POST.get('state', None)
        ssn_last_4 = request.POST.get('ssn_last4', None)
        created_on = int(round(time.time()))

        account = stripe.Account.retrieve(acc_id)
        external_account = {
            'object': 'bank_account',
            'account_number': acc_number,
            'country': country,
            'currency': 'USD',
            'routing_number': routing_number,
            'last4':ssn_last_4
        }
        account.external_account = external_account
        dob = {
            'day': day,
            'month': month,
            'year': year,
        }
        addr = {
            'city':city,
            'country':country,
            'line1':address,
            'postal_code':postal_code,
            'state':state
        }
        nameStr = proname.split()

        first_name = nameStr[0]
        try:
            last_name = nameStr[1]
        except:
            last_name = ''

        legal = {
            'dob':dob,
            'address':addr,
            'first_name': first_name,
            'last_name': last_name,
            'type': 'individual',
            'personal_id_number_provided':True,
            'ssn_last_4_provided':True,
            'business_tax_id_provided':False
        }
        tos = {
            'date': created_on,
            'ip': '75.70.234.51'
        }

        # account.legal_entity = legal
        account.tos_acceptance = tos
        account.save()

        adminid = request.session['manager_id']
        response = post_info(settings.SERVER_URL + '/getProviderByAdminID', {'adminID': adminid})
        result = response.get('result_code')
        if result == '0':
            providerInfo = response.get('provider_info')
            for info in providerInfo:
                if info['proEmail'] == proemail:
                    provider = Provider()
                    provider.proid = info['proid']
                    provider.proFirstName = info['proFirstName']
                    provider.proLastName = info['proLastName']
                    provider.proEmail = info['proEmail']
                    provider.proProfileImageUrl = info['proProfileImageUrl']
                    provider.proToken = info['proToken']

                    if len(account['id']) > 0:
                        response = post_info(settings.SERVER_URL + '/account_update_required',
                                             {'email': provider.proEmail})
                        result = response.get('status')
                        if result == 'success':
                            response = post_info(settings.SERVER_URL + '/updateProviderToken', {'proid':provider.proid, 'proToken':account.id})
                            result = response.get('result_code')
                            if result == '0':
                                return render(request, 'vacay/stripe_account.html',
                                          {'acc_id': account.id, 'provider': provider, 'note': 'success'})
                        else:
                            return render(request, 'vacay/stripe_account.html',
                                          {'acc_id': acc_id, 'provider': provider, 'error': 'failed'})
                    else:
                        return render(request, 'vacay/stripe_account.html',
                                      {'acc_id': acc_id, 'provider': provider, 'error': 'failed'})
        else:
            return HttpResponse('<h2>Server failed</h2>')

    elif request.method == 'GET':
        pass

def bmanager_payment(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    adminemail = request.session['manager_email']
    users = AdminUser.objects.filter(adminEmail=adminemail)
    me = users[0]
    response = post_info(settings.SERVER_URL + '/account_details', {'email': adminemail})
    result = response.get('status')
    if result == 'success':
        accountInfo = response.get('account_data')
        sts = accountInfo['status']
        accountid = accountInfo['accountid']
        if sts.startswith('Pending'):
            return render(request, 'vacay/manager_payment_account.html',
                          {'acc_id': accountid, 'me': me, 'pending': 'true'})
        else:
            type = request.session['manager']
            if type == 'beauty':
                return render(request, 'vacay/beautymanager_home.html', {'me': me, 'verified':'true'})
            elif type == 'retail':
                return render(request, 'vacay/retailmanager_home.html', {'me': me, 'verified':'true'})
            elif type == 'company':
                return render(request, 'vacay/companymanager_home.html', {'me': me, 'verified':'true'})
    elif result == 'error':
        account = stripe.Account.create(
            type="custom",
            country="US",
            email=adminemail
        )
        account_id = account['id']
        param = {
            'stripe_id': account_id,
            'email': adminemail,
            'country': 'US'
        }
        response = post_info(settings.SERVER_URL + '/account_create', param)
        result = response.get('result')
        if result == 'success':
            return render(request, 'vacay/manager_payment_account.html',
                          {'acc_id': account_id, 'me': me, 'created': 'true'})
        else:
            return HttpResponse('Payment account creation failed...')
    else:
        return redirect('/home')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def bpayment_update(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    if request.method == 'POST':
        email = request.POST.get('email', None)
        name = request.POST.get('name', None)

        acc_id = request.POST.get('acc_id', None)
        acc_number = request.POST.get('bank_number', None)
        country = request.POST.get('country', None)
        routing_number = request.POST.get('routing_number', None)
        day = request.POST.get('day', None)
        month = request.POST.get('month', None)
        year = request.POST.get('year', None)
        city = request.POST.get('city', None)
        address = request.POST.get('address', None)
        postal_code = request.POST.get('postal', None)
        state = request.POST.get('state', None)
        ssn_last_4 = request.POST.get('ssn_last4', None)
        created_on = int(round(time.time()))

        account = stripe.Account.retrieve(acc_id)
        external_account = {
            'object': 'bank_account',
            'account_number': acc_number,
            'country': country,
            'currency': 'USD',
            'routing_number': routing_number,
            'last4':ssn_last_4
        }
        account.external_account = external_account
        dob = {
            'day': day,
            'month': month,
            'year': year,
        }
        addr = {
            'city':city,
            'country':country,
            'line1':address,
            'postal_code':postal_code,
            'state':state
        }
        nameStr = name.split()

        first_name = nameStr[0]
        try:
            last_name = nameStr[1]
        except:
            last_name = ''

        legal = {
            'dob':dob,
            'address':addr,
            'first_name': first_name,
            'last_name': last_name,
            'type': 'individual',
            'personal_id_number_provided':True,
            'ssn_last_4_provided':True,
            'business_tax_id_provided':False
        }
        tos = {
            'date': created_on,
            'ip': '75.70.234.51'
        }

        # account.legal_entity = legal
        account.tos_acceptance = tos
        account.save()
        users = AdminUser.objects.filter(adminEmail=email)
        me = users[0]
        if len(account['id']) > 0:
            response = post_info(settings.SERVER_URL + '/account_update_required',
                                 {'email': email})
            result = response.get('status')
            if result == 'success':
                return render(request, 'vacay/manager_payment_account.html',
                            {'acc_id': account.id, 'me': me, 'note': 'success'})
            else:
                return render(request, 'vacay/manager_payment_account.html',
                              {'acc_id': acc_id, 'me': me, 'error': 'failed'})
        else:
            return render(request, 'vacay/manager_payment_account.html',
                          {'acc_id': acc_id, 'me': me, 'error': 'failed'})

    elif request.method == 'GET':
        pass


def managerprofile(request):
    eml = request.session['manager_email']
    users = AdminUser.objects.filter(adminEmail=eml)
    me = users[0]
    return render(request, 'vacay/manager_profile.html', {'me':me})

def retailmenu(request):
    return render(request, 'vacay/retailmenu.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getretailinfo(request):
    if request.method == 'GET':
        retailList = []
        category = request.GET['category']
        request.session['retailcategory'] = category
        if category == 'Skiing':
            category = 'Skiing & Snowboarding'
        response = post_info(settings.SERVER_URL + '/getBroadmoorInfo', {'bm_proCategory':category})
        result = response.get('result_code')
        if result == '0':
            retailInfo = response.get('broadmoor_info')
            for info in retailInfo:
                retail = RetailProduct()
                retail.retailid = info['bm_proid']
                retail.adminID = info['adminID']
                retail.adminEmail = info['adminEmail']
                retail.adminLogo = info['adminLogoImageUrl']
                retail.name = info['bm_proName']
                retail.image = info['bm_proImageUrl']
                retail.inventorynum = info['bm_proInventoryNum']
                retail.category = info['bm_proCategory']
                retail.additional = info['bm_proAdditional']

                if retail.adminEmail == request.session['manager_email']:
                    retailList.insert(0, retail)
            request.session['retailcategory'] = category
            return render(request, 'vacay/retaillist.html', {'retails':retailList})
        else:
            return redirect('/retailmenu')

def retaildetail(request, retailid):
    category = request.session['retailcategory']
    response = post_info(settings.SERVER_URL + '/getBroadmoorInfo', {'bm_proCategory': category})
    result = response.get('result_code')
    if result == '0':
        retailInfo = response.get('broadmoor_info')
        for info in retailInfo:
            if info['bm_proid'] == retailid:
                retail = RetailProduct()
                retail.retailid = info['bm_proid']
                retail.adminID = info['adminID']
                retail.adminEmail = info['adminEmail']
                retail.adminLogo = info['adminLogoImageUrl']
                retail.name = info['bm_proName']
                retail.image = info['bm_proImageUrl']
                retail.inventorynum = info['bm_proInventoryNum']
                retail.category = info['bm_proCategory']
                retail.additional = info['bm_proAdditional']

                request.session['retail_id'] = retailid

                response = post_info(settings.SERVER_URL + '/getBroadmoorDetailInfo', {'bm_proid':retail.retailid})
                result = response.get('result_code')
                if result == '0':
                    sizeList = []
                    sizeInfo = response.get('detail_info')
                    for info in sizeInfo:
                        detail = RetailDetail()
                        detail.detailid = info['bm_detailID']
                        detail.proid = info['bm_proid']
                        detail.size = info['bm_proSize']
                        detail.price = info['bm_proPrice']
                        detail.quantity = info['bm_proQuantity']
                        sizeList.append(detail)

                    return render(request, 'vacay/retaildetail.html', {'retail':retail, 'sizes':sizeList})
    else:
        return HttpResponse('<h2>Server Error!</h2>')

def retail_media(request, retailid):
    data = {
        'item_id': retailid,
        'item': 'bproduct'
    }
    serviceMedia = get_info(settings.SERVER_URL + "/get_media", data)
    result = serviceMedia.get('result_code')
    if result == '0':
        media = serviceMedia.get('media')
        md = Media()
        md.video = media['video_url']
        md.youtube = media['youtube_url']
        md.imageA = media['image_a']
        md.imageB = media['image_b']
        md.imageC = media['image_c']
        md.imageD = media['image_d']
        md.imageE = media['image_e']
        md.imageF = media['image_f']

        return render(request, 'vacay/announce_media.html', {'media': md})
    else:
        return redirect('/retaildetail/' + request.session['retail_id'])

def employees(request):
    emList = []
    response = post_info(settings.SERVER_URL + '/getAllEmployeeByAdminID', {'adminID':request.session['manager_id']})
    result = response.get('result_code')
    if result == '0':
        emInfo = response.get('employee_info')
        for info in emInfo:
            employee = Employee()
            employee.em_id = info['em_id']
            employee.image = info['em_image']
            employee.name = info['em_name']
            employee.gender = info['em_gender']
            employee.password = info['em_password']
            employee.email = info['em_email']
            employee.millennial = info['em_millennial']
            employee.givenbuck = info['em_givenbuck']
            employee.usedbuck = info['em_usedbuck']
            employee.interaction = info['em_interaction']
            employee.status = info['em_status']

            emList.insert(0, employee)
        return render(request, 'vacay/employees.html', {'employees':emList})
    else:
        return redirect('/home')

def chatemployee(request):
    email = request.GET['email']
    response = post_info(settings.SERVER_URL + '/getAllEmployeeByAdminID', {'adminID': request.session['manager_id']})
    result = response.get('result_code')
    if result == '0':
        emInfo = response.get('employee_info')
        for info in emInfo:
            if info['em_email'] == email:
                friend_email = info['em_email']
                # return HttpResponse(friend_email)
                friend_name = info['em_name']
                friend_photo = info['em_image']

                request.session['friend_email'] = friend_email
                request.session['friend_name'] = friend_name
                request.session['friend_photo'] = friend_photo

                friend = CommonUser()
                nameStr = friend_name.split()

                first_name = nameStr[0]
                try:
                    last_name = nameStr[1]
                except:
                    last_name = ''
                friend.first_name = first_name
                friend.last_name = last_name
                friend.email = friend_email
                friend.photo_url = friend_photo
                eml = ''
                if request.session['manager_email'] != '':
                    users = AdminUser.objects.filter(adminEmail=request.session['manager_email'])
                    me = CommonUser()
                    me.userid = users[0].adminID
                    name = users[0].adminName
                    nameStr = name.split()
                    first_name = nameStr[0]
                    try:
                        last_name = nameStr[1]
                    except:
                        last_name = ''
                    me.first_name = first_name
                    me.last_name = last_name
                    me.email = users[0].adminEmail
                    me.photo_url = users[0].adminImageUrl

                    return render(request, 'vacay/chat.html', {'me': me, 'friend': friend})
                else:
                    return redirect('/home')

def signmailemployee(request):
    employee_id = request.GET['employee_id']
    response = post_info(settings.SERVER_URL + '/sendEmEmailfromApp', {'em_id':employee_id})
    result = response.get('result_code')
    if result == '0':
        context = {'item': 'sendmailtoemployee', 'response': 'Success!'}
        return render(request, 'vacay/result.html', context)
    else:
        context = {'item': 'sendmailtoemployee', 'response': 'Mailing failed!'}
        return render(request, 'vacay/result.html', context)

def companyjobs(request):
    jobList = get_jobInfo(request.session['manager_id'])
    return render(request, 'vacay/job_list.html', {'jobs':jobList, 'manager':'true'})

def companyannounces(request):
    announceList = get_announceInfo(request.session['manager_id'])
    return render(request, 'vacay/announce_list.html', {'announces': announceList, 'manager': 'true'})

def respondeds(request):
    announceid = request.GET['announce_id']
    param = {
        'an_id': announceid,
        'adminID': request.session['manager_id']
    }
    response = get_info(settings.SERVER_URL + '/getEmployeeForAnnounce', param)
    result = response.get('result_code')
    if result == '0':
        emList = []
        respondedInfo = response.get('em_info')
        for info in respondedInfo:
            employee = Employee()
            employee.em_id = info['em_id']
            employee.email = info['em_email']
            employee.name = info['em_name']
            employee.image = info['em_image']

            emList.insert(0, employee)
        return render(request, 'vacay/announce_responded_list.html', {'respondeds': emList})

def recorder(request):
    return render(request, 'vacay/audio_recorder.html')

def activities(request):
    return render(request, 'vacay/activities_menu.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def actmenu(request):
    if request.method == 'POST':
        city = ''
        lat = ''
        lng = ''
        eml = request.session['fb_email']
        try:
            city = request.POST.get('city', '')
            lat = request.POST.get('lat', '')
            lng = request.POST.get('lng', '')
            activity = request.POST.get('activity', '')

            if city == '':
                users = Friend.objects.filter(email=eml)
                me = users[0]
                city = me.address
                lat = me.latitude
                lng = me.longitude

            request.session['mycity'] = city
            request.session['mylat'] = lat
            request.session['mylng'] = lng
            request.session['activity'] = activity
            return render(request, 'vacay/actmenu.html', {'activity': activity})

        except MultiValueDictKeyError:

            users = Friend.objects.filter(email=eml)
            me = users[0]
            city = me.address
            lat = me.latitude
            lng = me.longitude

            request.session['mycity'] = city
            request.session['mylat'] = lat
            request.session['mylng'] = lng
            return render(request, 'vacay/actmenu.html', {'activity': request.session['activity']})

    elif request.method == 'GET':
        activity = request.session['activity']
        return render(request, 'vacay/actmenu.html', {'activity': activity})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def act(request):
    if request.method == 'POST':
        item = request.POST.get('item', None)
        activity = request.session['activity']
        interest = activity
        if 'Run' in activity:
            interest = 'Run'
        elif 'Ski' in activity:
            interest = 'Ski & Snowboard'
        userList = []
        if item == 'allfriend':
            users = Friend.objects.all()
            if users.count() > 0:
                for user in users:
                    if user.email != request.session['fb_email']:
                        user.interests = "-" + user.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                                         "\n-").replace(
                            "\"", "").replace("[", "").replace("]", "")
                        if interest in user.interests:
                            userList.insert(0, user)
            return render(request, 'vacay/friends.html', {'friends': userList})
        elif item == 'nearbyfriend':
            users = Friend.objects.all()
            if users.count() > 0:
                for user in users:
                    if user.email != request.session['fb_email']:
                        user.interests = "-" + user.interests.replace("{", "").replace("}", "").replace("\",",
                                                                                                        "\n-").replace(
                            "\"", "").replace("[", "").replace("]", "")
                        if interest in user.interests and user.address == request.session['mycity']:
                            userList.insert(0, user)
            return render(request, 'vacay/friends.html', {'friends': userList})

        # elif item == 'shop':
        #     retailList = []
        #     if activity == 'Skiing':
        #         activity = 'Skiing & Snowboarding'
        #     response = post_info(settings.SERVER_URL + '/getBroadmoorInfo', {'bm_proCategory': activity})
        #     result = response.get('result_code')
        #     if result == '0':
        #         retailInfo = response.get('broadmoor_info')
        #         for info in retailInfo:
        #             retail = RetailProduct()
        #             retail.retailid = info['bm_proid']
        #             retail.adminID = info['adminID']
        #             retail.adminEmail = info['adminEmail']
        #             retail.adminLogo = info['adminLogoImageUrl']
        #             retail.name = info['bm_proName']
        #             retail.image = info['bm_proImageUrl']
        #             retail.inventorynum = info['bm_proInventoryNum']
        #             retail.category = info['bm_proCategory']
        #             retail.additional = info['bm_proAdditional']
        #
        #             retailList.insert(0, retail)
        #
        #         request.session['activity'] = activity
        #         return render(request, 'vacay/retaillist.html', {'retails': retailList, 'buy':'true'})
        else:
            return redirect('/home')

def retail2detail(request, retailid):
    activity = request.session['activity']
    employee = ''
    if request.session['em_email'] != '':
        employee = 'true'
    if activity == 'Skiing':
        activity = 'Skiing & Snowboarding'
    response = post_info(settings.SERVER_URL + '/getBroadmoorInfo', {'bm_proCategory': activity})
    result = response.get('result_code')
    if result == '0':
        retailInfo = response.get('broadmoor_info')
        for info in retailInfo:
            if info['bm_proid'] == retailid:
                retail = RetailProduct()
                retail.retailid = info['bm_proid']
                retail.adminID = info['adminID']
                retail.adminEmail = info['adminEmail']
                retail.adminLogo = info['adminLogoImageUrl']
                retail.name = info['bm_proName']
                retail.image = info['bm_proImageUrl']
                retail.inventorynum = info['bm_proInventoryNum']
                retail.category = info['bm_proCategory']
                retail.additional = info['bm_proAdditional']

                request.session['retail_id'] = retailid
                request.session['retail_email'] = retail.adminEmail

                response = post_info(settings.SERVER_URL + '/getBroadmoorDetailInfo', {'bm_proid':retail.retailid})
                result = response.get('result_code')
                if result == '0':
                    sizeList = []
                    sizeInfo = response.get('detail_info')
                    for info in sizeInfo:
                        detail = RetailDetail()
                        detail.detailid = info['bm_detailID']
                        detail.proid = info['bm_proid']
                        detail.size = info['bm_proSize']
                        detail.price = info['bm_proPrice']
                        detail.quantity = info['bm_proQuantity']
                        sizeList.append(detail)

                    return render(request, 'vacay/retaildetail2.html', {'retail':retail, 'sizes':sizeList, 'employee':employee})
    else:
        return HttpResponse('<h2>Server Error!</h2>')

def checkretailpayment(request):
    # return render(request, 'vacay/stripe_payment.html')
    price = request.GET['totalprice']
    request.session['price'] = price
    retailemail = request.session['retail_email']
    response = post_info(settings.SERVER_URL + '/account_details', {'email': retailemail})
    result = response.get('status')
    if result == 'success':
        accountInfo = response.get('account_data')
        sts = accountInfo['status']
        accountid = accountInfo['accountid']
        request.session['admin_token'] = accountid
        if sts.startswith('Pending'):
            context = {'item': 'checkretailpayment', 'response': 'Sorry, this retailer\'s payment isn\'t verified.'}
            return render(request, 'vacay/result.html', context)
        else:
            price = float(price.replace('$', '').replace(',', '')) * 100
            return render(request, 'vacay/stripe_payment.html', {'price': price, 'retail':'true'})

    elif result == 'error':
        context = {'item': 'checkretailpayment', 'response': 'Sorry, this retailer\'s payment isn\'t verified.'}
        return render(request, 'vacay/result.html', context)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def paytoretailer(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    if request.method == "POST":

        token = request.POST.get('token', None)

        # return HttpResponse(token)
        adminToken = request.session['admin_token']

        if adminToken is not None and adminToken != '':
            amount = request.session['price']
            amount = amount.replace('$', '').replace(',', '')
            amount = int(float(amount) * 100)

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token  # obtained with Stripe.js
            )
            if charge is not None:
                retailerOffer = int(amount * 0.8)
                transfer = stripe.Transfer.create(
                    amount=retailerOffer,
                    currency="usd",
                    destination=adminToken
                )
                if transfer is not None:
                    # ownerOffer2 = int(amount * 0.2)
                    # transfer2 = stripe.Transfer.create(
                    #     amount=ownerOffer2,
                    #     currency="usd",
                    #     destination='ownerToken'     ##########################################################################################################
                    # )
                    paid_money = request.session['price']
                    data = {}
                    if request.session['em_email'] != '':
                        data = {
                            'senderEmail': request.session['em_email'],
                            'receiverEmail': request.session['retail_email'],
                            'paidMoney': paid_money.replace('$', '').replace(',', '')
                        }
                    elif request.session['fb_email'] != '':
                        data = {
                            'senderEmail': request.session['fb_email'],
                            'receiverEmail': request.session['retail_email'],
                            'paidMoney': paid_money.replace('$', '').replace(',', '')
                        }
                    response = post_info(settings.SERVER_URL + '/savePaySendMail', data)
                    result = response.get('result')
                    if result == '0':
                        if request.session['em_email'] != '':
                            users = Employee.objects.filter(email=request.session['em_email'])
                            em_id = users[0].em_id
                            data = {
                                'em_id': em_id,
                                'amount': paid_money.replace('$', '').replace(',', '')
                            }
                            response = post_info(settings.SERVER_URL + '/addEmUsedBuck', data)
                        return render(request, 'vacay/stripe_payment.html', {'note': 'success'})
                    return render(request, 'vacay/stripe_payment.html', {'note': 'success'})
                else:
                    return render(request, 'vacay/stripe_payment.html', {'transfer_error': 'failed'})
            else:
                return render(request, 'vacay/stripe_payment.html', {'charge_error': 'failed'})
        else:
            return render(request, 'vacay/stripe_payment.html', {'seller_error': 'unverified'})

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def linkedin_login(request):
    if request.method == 'POST':
        try:
            request.session['fb_first_name'] = request.POST.get('fb_first_name', None)
            request.session['fb_last_name'] = request.POST.get('fb_last_name', None)
            request.session['fb_email'] = request.POST.get('fb_email', None)
            request.session['fb_photo'] = request.POST.get('fb_photo', None)
            request.session['fb_gender'] = request.POST.get('fb_gender', None)
            tosurvey = request.POST.get('tosurvey', None)
            if tosurvey == 'true':
                request.session['user'] = 'common'
                context = {'registered': 'false'}
                users = Friend.objects.filter(email=request.session['fb_email'])
                if users.count() > 0:
                    context = {'registered': 'true'}
                return render(request, 'vacay/login_survey.html', context)
            else:
                return render(request, 'vacay/linkedin_login.html', {'fb': 'true'})
        except AssertionError:
            return render(request, 'vacay/linkedin_login.html')

def linkedin(request):
    return render(request, 'vacay/linkedin_login.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getlinkedin(request):
    if request.method == 'POST':

        request.session['ln_job'] = request.POST.get('lnjob', None)
        tofb = request.POST.get('tofb', None)

        if tofb == 'true':
            return render(request, 'vacay/welcome.html', {'ln': 'true'})
        elif tofb == 'false':
            request.session['user'] = 'common'
            context = {'registered': 'false'}
            users = Friend.objects.filter(email=request.session['fb_email'])
            if users.count() > 0:
                context = {'registered': 'true'}
            return render(request, 'vacay/login_survey.html', context)

def getinfo(request):
    category = request.GET['category']
    request.session['wc_category'] = category
    tips = Watercooler.objects.filter(company='common', category=category).order_by('-id')
    users = Friend.objects.filter(email=request.session['fb_email'])
    me = users[0]
    if category == 'Dating Tips(Audience Specific)' or category == 'Dating Questions(Audience Specific)':
        tips = Watercooler.objects.filter(company='common', category=category, gender=me.gender).order_by('-id')
        return render(request, 'vacay/info_list.html', {'infos': tips, 'category': category})
    elif category == 'General Questions(All Audiences)':
        return render(request, 'vacay/info_list.html', {'infos': tips, 'category': category})
    else:
        return render(request, 'vacay/info_list.html', {'infos': tips, 'category': category})


def testpay(request):
    return render(request, 'vacay/testpay.html')









































































































#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def weather(request):
    if request.session['em_email'] != '':
        data = {'email': request.session['em_email']}
        userInfo = get_info(settings.SERVER_URL + "/getUserProfile", data)
        result_code = userInfo['result_code']
        if result_code == '0':
            city = userInfo['user_profile'][0]['address']
            result = decode_address_to_coordinates(city)
            if result is not None:
                lat = result["lat"]
                lng = result["lng"]
                weather_url = "https://darksky.net/forecast/" + str(lat) + "," + str(lng) + "/si12/en"
                return redirect(weather_url)
            else:
                return render(request, 'vacay/home.html', {'me_email': request.session['em_email']})
        else:
            return render(request, 'vacay/home.html', {'me_email': request.session['em_email']})
    elif request.session['pro_email'] != '':
        providers = Provider.objects.filter(proEmail=request.session['pro_email'])
        me = providers[0]
        me_city = me.proCity
        city = me_city
        result = decode_address_to_coordinates(city)
        if result is not None:
            lat = result["lat"]
            lng = result["lng"]
            weather_url = "https://darksky.net/forecast/" + str(lat) + "," + str(lng) + "/si12/en"
            return redirect(weather_url)
        else:
            return render(request, 'vacay/provider_home.html', {'me': me})

googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

def decode_address_to_coordinates(address):
        params = {
                'address' : address,
                'sensor' : 'false',
        }
        url = 'http://maps.google.com/maps/api/geocode/json?' + urllib.parse.urlencode(params)
        response = urllib.request.urlopen(url)
        a = response.read()
        encoding = response.info().get_content_charset('utf8')
        data = json.loads(a.decode(encoding))
        try:
            dt = data["results"][0]["geometry"]["location"]
            return dt
        except:
            return None


def show_weather(request):
    return render(request, 'vacay/weather.html')

def nearby(request):
    return render(request, 'vacay/map_nearby.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def services_nearby(request):

    if request.method == 'POST':

        try:
            lat = request.POST.get('latitude', None)
            lng = request.POST.get('longitude', None)
            service_type = request.POST.get('types', None)
            range = request.POST.get('ranges', None)
            address = request.POST.get('address', None)

            if lat is None or lng is None or service_type is None or range is None:
                return render(request, 'vacay/result.html', {'response':'Error! Try again'})

            if service_type == 'All...':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address}
                return render(request, 'vacay/nearby_service.html', context)
            elif service_type == 'Hospital':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address}
                return render(request, 'vacay/nearby_hospital.html', context)
            elif service_type == 'Airport':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address}
                return render(request, 'vacay/nearby_airport.html', context)
            elif service_type == 'Restaurant':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address}
                return render(request, 'vacay/nearby_restaurant.html', context)
            elif service_type == 'Bank':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address}
                return render(request, 'vacay/nearby_bank.html', context)
            elif service_type == 'Beauty-Salon':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address}
                return render(request, 'vacay/nearby_beauty.html', context)
            elif service_type == 'Accounting':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'accounting'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Bar':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'bar'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Cafe':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'cafe'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Amusementpark':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'amusementpark'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Bookstore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'bookstore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Busstation':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'busstation'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Bicyclestore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'bicyclestore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Campground':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'campground'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Carrepair':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'carrepair'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Carrental':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'carrental'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Carwash':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'carwash'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Cardealer':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'cardealer'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Casino':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'casino'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Church':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'church'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Cityhall':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'cityhall'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Clothingstore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'clothingstore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Conveniencestore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'conveniencestore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Courthouse':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'courthouse'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Departmentstore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'departmentstore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Dentist':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'dentist'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Doctor':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'doctor'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Electrician':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'electrician'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Electronicsstore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'electronicsstore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Embassy':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'embassy'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Firestation':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'firestation'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Florist':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'florist'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'Furniturestore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'furniturestore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'gasstation':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'gasstation'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'gym':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'gym'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'haircare':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'haircare'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'hardwarestore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'hardwarestore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'hindutemple':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'hindutemple'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'homegoodsstore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'homegoodsstore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'aquarium':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'aquarium'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'artgallery':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'artgallery'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'atm':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'atm'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'bakery':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'bakery'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'bowlingalley':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'bowlingalley'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'insuranceagency':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'insuranceagency'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'jewelrystore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'jewelrystore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'laundry':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'laundry'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'lawyer':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'lawyer'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'library':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'library'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'liquorstore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'liquorstore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'localgovernmentoffice':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'localgovernmentoffice'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'locksmith':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'locksmith'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'lodging':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'lodging'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'mealdelivery':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'mealdelivery'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'mealtakeaway':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'mealtakeaway'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'mosque':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'mosque'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'movierental':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'movierental'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'movietheater':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'movietheater'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'movingcompany':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'movingcompany'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'museum':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'museum'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'nightclub':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'nightclub'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'painter':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'painter'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'park':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'park'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'parking':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'parking'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'petstore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'petstore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'pharmacy':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'pharmacy'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'physiotherapist':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'physiotherapist'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'placeofworship':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'placeofworship'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'plumber':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'plumber'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'police':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'police'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'postoffice':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'postoffice'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'realestateagency':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'realestateagency'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'roofingcontractor':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'roofingcontractor'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'rvpark':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'rvpark'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'shoestore':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'shoestore'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'shoppingmall':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'shoppingmall'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'spa':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'spa'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'stadium':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'stadium'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'storage':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'storage'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'store':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'store'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'subwaystation':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'subwaystation'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'synagogue':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'synagogue'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'taxistand':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'taxistand'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'trainstation':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'trainstation'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'transitstation':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'transitstation'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'travelagency':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'travelagency'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'university':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'university'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'veterinarycare':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'veterinarycare'}
                return render(request, 'vacay/nearby.html', context)
            elif service_type == 'zoo':
                context = {'latitude': str(lat), 'longitude': str(lng), 'range': str(range), 'address': address,
                           'type': 'zoo'}
                return render(request, 'vacay/nearby.html', context)
        except AssertionError:
            return render(request, 'vacay/result.html', {'response': 'Error! Try again.'})
        except MultiValueDictKeyError:
            return render(request, 'vacay/result.html', {'response': 'Error! Try again.'})

    else:
        return render(request, 'vacay/result.html', {'response':'Error! Try again.'})

















