from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
import re
from .models import UserInfo
from .models import RegistrationQueue
import requests
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt


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

        if RegistrationQueue.objects.filter(email=emailReg).exists():

            data={
                'status': 'under review'
            }

        else:
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
                """
                response = requests.get('https://api.trumail.io/v2/lookups/json?email=' + emailReg)
                emailVerifier = response.json()

                try:
                    emailVerifierMessage = emailVerifier['Message']
                except Exception as e:
                    emailVerifierMessage = "none"

                try:
                    emailVerifierDel = emailVerifier['deliverable']
                except Exception as e:
                    emailVerifierDel = False

                if emailVerifierMessage == 'No response received from mail server':
                    data={
                    'status': "email not exist"
                    }

                elif emailVerifierDel == True:
                    #legit email
                    result = sendConfirmationUser(emailReg)
                    data={
                    'status': 'success'
                    }

                    #send confirmation to admin
                    #sendConfirmationAdmin(emailReg)
                else:
                    #email non-existent
                    data={
                    'status': "email not exist"
                    }
                    """
                sendConfirmationAdmin(emailReg, request)

                #store to Registration DB
                RegistrationQueue.objects.create(email=emailReg, password=passwordReg)

                data={
                'status': 'success'
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
def sendConfirmationAdmin(email, request):
    subject = 'Requesting an account for Text Trainer and Classifier Tool'
    from_email = settings.EMAIL_HOST_USER
    send_to = settings.SEND_TO
    message = " "

    ctx = {
        'emailAdmin': send_to[0],
        'emailUser': email
    }

    emailMessage = render_to_string('Webapp/confirmAccountFromEmail.html', ctx, request=request)

    mail = EmailMultiAlternatives(subject, message, from_email, send_to)

    mail.attach_alternative(emailMessage, 'text/html')

    try:
        mail.send()
    except:
        echo("Unable to send mail.")

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

@csrf_exempt
#Email Confirmed/Denied by Admin
def confirmAccount(request):
    if request.method == 'POST':
        adminEmail = request.POST['myemail']
        choiceValue = request.POST['choice']
        userEmail = request.POST['userMail']

        checkPass = settings.SEND_TO
        print(adminEmail)
        print(checkPass[0])
        print(choiceValue)
        print(userEmail)

        if adminEmail == checkPass[0]:
            if choiceValue == 'accept':
                print('Right here')
                query = RegistrationQueue.objects.filter(email=userEmail)
                confirmPass = query[0].password
                UserInfo.objects.create(email=userEmail, password=confirmPass)

                #sucess page
                result = 'Webapp/RegSuccess.html'
        else:
            #404 Not Found
            result = 'Webapp/404NotFound.html'
    else:
        #404 Not Found
        result = 'Webapp/404NotFound.html'

    return render(request, result)
