from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
import re
from .models import UserInfo

#Home Page
def base(request):
    return render(request, 'Webapp/base.html')

#Log-in Validator
def logIn(request):
    if request.method == 'POST':
        emailIn = request.POST['emailIn']
        passwordIn = request.POST['passwordIn']

        if UserInfo.objects.filter(email=emailIn).exists() and UserInfo.objects.filter(password=passwordIn).exists():
            data = {
            'status' : 'success'
            }

            request.session['userEmail'] = emailIn
        else:
            data = {
            'status' : 'invalid credential'
            }
    else:
        data = {
        'status' : 'error request'
        }

    return JsonResponse(data)

#Log-out
def logOut(request):
    del request.session['userEmail']

    data = {
        'status': 'success'
    }

    return JsonResponse(data)

#Registration Validator
def validateRegForm(request):
    if request.method == 'POST':
        emailReg = request.POST['emailReg']
        passwordReg = request.POST['passwordReg']

        flag = 0

        if (len(passwordReg)<8):
            flag = -1
        elif not re.search("[a-z]", passwordReg):
            flag = -1
        elif not re.search("[A-Z]", passwordReg):
            flag = -1
        elif not re.search("[0-9]", passwordReg):
            flag = -1
        elif not re.search("[_@$]", passwordReg):
            flag = -1
        elif re.search("\s", passwordReg):
            flag = -1
        else:
            flag = 0

        if flag == 0:
            # pass success
            #verify email legitimacy
            result = sendConfirmationUser(emailReg)

            if result == 0:
                #legit email
                data={
                'status': 'success'
                }
                #send confirmation to admin
                sendConfirmationAdmin(emailReg)

            else:
                #email non-existent
                data={
                'status': "email not exist"
                }
        else:
            # pass failed
            data={
            'status': 'invalid password'
            }


    else:
        data = {
        'status': 'error request'
        }

    return JsonResponse(data)

#Send Confirmation Email to Admin
def sendConfirmationAdmin(email):
    subject = 'Requesting an account for Text Trainer and Classifier Tool'
    message = email + ' is requesting for an account. Will you accept? \n Yes or No?'
    from_email = settings.EMAIL_HOST_USER
    send_to = settings.SEND_TO

    send_mail(subject, message, from_email, send_to, fail_silently=True)

#Verify Email Registration
def sendConfirmationUser(email):
    subject = 'Text Trainer and Classifier Tool Notification'
    message = 'Thank you for signing up. An admin will verify your account. \n We will notify you once your account has been reviewed.'
    from_email = settings.EMAIL_HOST_USER
    send_to = [email]

    try:
        send_mail(subject, message, from_email, send_to, fail_silently=False)
        result = 0
    except:
        result = 1

    return result

#Email Confirmed/Denied by Admin
