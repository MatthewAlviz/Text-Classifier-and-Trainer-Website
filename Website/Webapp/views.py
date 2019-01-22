from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
import re
from .models import UserInfo
from .models import RegistrationQueue
from .models import ChangePassQueue
from .models import TrainedModels
import requests
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import uuid
import math
import json
import random
import os

#MachineLearning libs
#import library
import fastText
import pandas as pd
import re
from nltk.corpus import stopwords
from io import StringIO
import csv
homeURL = 'http://0.0.0.0:8000/'

#Home Page
def base(request):

    if 'email' in request.COOKIES:
        value = request.COOKIES['email']
        if value != 'NaN':
            request.session['userEmail'] = value

    if request.session.has_key('userEmail'):

        try:
            remember = request.GET['keep']
        except:
            remember = "false"

        username = request.session['userEmail']

        if TrainedModels.objects.filter(email=username).exists():

            query = TrainedModels.objects.filter(email=username)
            count = query.count()

            return render(request, 'Webapp/loggedInWithModels.html', {"username": username, "remember": remember, "numOfModels": count, "models": query})
        else:
            return render(request, 'Webapp/loggedIn.html', {"username": username, "remember": remember})
    else:
        return render(request, 'Webapp/base.html')

#Log-in Validator
def logIn(request):
    if request.method == 'POST':
        emailIn = request.POST['emailLog']
        passwordIn = request.POST['passwordLog']

        if UserInfo.objects.filter(email=emailIn).exists() and UserInfo.objects.filter(password=passwordIn).exists():

            request.session['userEmail'] = emailIn
            data = {
            'status' : 'success'
            }
        else:
            data = {
            'status' : 'invalid credential'
            }
    else:
        data = {
        'status' : 'error request'
        }

    return JsonResponse(data)

#Forgot password
def forgotPass(request):
    if request.method == 'POST':
        reqUser = request.POST['emailForgot']
        if UserInfo.objects.filter(email=reqUser).exists():
            #Add to Queue
            if ChangePassQueue.objects.filter(email=reqUser).exists():
                query = ChangePassQueue.objects.filter(email=reqUser)
                count = query[0].reqCount
                count += 1

                if count <= 5:
                    #Email to user change password
                    id = query[0].ticketNo
                    sendForgotPassToUser(reqUser, id)

                    data = {
                    'status' : 'success'
                    }

                else:
                    #Exceeded change pass limit
                    data = {
                    'status' : 'limit exceeded'
                    }
            else:
                id = uuid.uuid4().hex
                query = UserInfo.objects.get(email=reqUser)
                ChangePassQueue.objects.create(ticketNo=id,email=query,reqCount=1)

                #Email to user change password
                sendForgotPassToUser(reqUser, id)

                data = {
                'status' : 'success'
                }
        else:
            data = {
            'status' : 'invalid credential'
            }

        return JsonResponse(data)

#Send Forgot Pass Email
def sendForgotPassToUser(email, id):
    subject = 'Text Trainer and Classifier Tool Notification'
    message = 'Click the link below to change your password:\n ' + homeURL + 'changePass/?id=' + id
    from_email = settings.EMAIL_HOST_USER
    send_to = [email]

    send_mail(subject, message, from_email, send_to, fail_silently=False)

#Change password page
def changePass(request):
    try:
        id = request.GET['id']
        if ChangePassQueue.objects.filter(ticketNo=id).exists():
            query = ChangePassQueue.objects.get(ticketNo=id)
            username = query.email.email
            return render(request, 'Webapp/changePass.html', {"username": username})
        else:
            return render(request, 'Webapp/404NotFound.html')

    except:
        return render(request, 'Webapp/404NotFound.html')

#Verify change password
def verifyPass(request):
    if request.method == 'POST':
        if ChangePassQueue.objects.filter(ticketNo=id).exists():

            id = request.POST['id']
            email = request.POST['changeMe']
            newPass = request.POST['passwordChange']

            flag = 0

            if (len(newPass)<8):
                flag = -1
            elif not re.search("[a-z]", newPass):
                flag = -1
            elif not re.search("[A-Z]", newPass):
                flag = -1
            elif not re.search("[0-9]", newPass):
                flag = -1
            elif not re.search("[_@$]", newPass):
                flag = -1
            elif re.search("\s", newPass):
                flag = -1
            else:
                flag = 0

            if flag == 0:
                #delete Queue
                ChangePassQueue.objects.filter(ticketNo=id).delete()

                #update User Info
                UserInfo.objects.filter(email=email).update(password=newPass)

                data={
                'status' : 'success'
                }

            else:
                data={
                'status' : 'invalid'
                }
        else:
            data={
            'status' : 'expired'
            }
    return JsonResponse(data)

@csrf_exempt
#Keep Me Logged In
def keepLoggedIn(request):
    if request.method == 'POST':
        remember = request.POST['keepLogged']
        myUserEmail = request.POST['myUserEmail']

        if remember == 'true':
            #Save to cookies
            response = HttpResponse("hello")
            response.set_cookie('email', myUserEmail)

            return response
        else:
            data = {
            'status' : 'false'
            }

            return JsonResponse(data)
@csrf_exempt
#Log-out
def logOut(request):
    del request.session['userEmail']
    response = HttpResponse("hello")
    response.set_cookie('email', 'NaN')

    return response

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
                #verify email legitimacy (COMING SOON!)
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

        if RegistrationQueue.objects.filter(email=userEmail).exists():
            if adminEmail == checkPass[0]:
                subject = 'Text Trainer and Classifier Tool Notification'
                from_email = settings.EMAIL_HOST_USER
                send_to = [userEmail]

                if choiceValue == 'accept':
                    query = RegistrationQueue.objects.filter(email=userEmail)
                    confirmPass = query[0].password
                    UserInfo.objects.create(email=userEmail, password=confirmPass)

                    #email accepted to user
                    message = 'Thank you for signing up. Your account has been verified. \n You may now log in.'
                else:
                    #email not accepted to user
                    message = 'Thank you for signing up. Unfortunately your registration has been declined. \n Please contact the admin if you have any concerns.'

                    #sucess page
                send_mail(subject, message, from_email, send_to, fail_silently=False)
                result = 'Webapp/RegSuccess.html'
            else:
                #404 Not Found
                result = 'Webapp/404NotFound.html'
        else:
            result = 'Webapp/404NotFound.html'
    else:
        #404 Not Found
        result = 'Webapp/404NotFound.html'

    #delete registration queue
    deleteThis = RegistrationQueue.objects.filter(email=userEmail)
    deleteThis.delete()

    return render(request, result)

def searchModelsPage(request):
    try:
        searchID = request.GET['search']
        query = TrainedModels.objects.filter(modelTitle__icontains=searchID)
    except:
        query = TrainedModels.objects.all()

    username = request.session.get('userEmail', 'nothing')

    pages = query.count() / 6
    a,b = math.modf(pages)
    if(int(b) == 0):
        pages = 1
    else:
        pages = int(b)

    if username != 'nothing':
        return render(request, 'Webapp/searchForModels.html', {"username": username, "models": query, "numOfModels": query.count(), "numOfPages": pages})
    else:
        return render(request, 'Webapp/searchForModels2.html', {"models": query, "numOfModels": query.count(), "numOfPages": pages})

def models_autocomplete(request):
    if request.is_ajax():
        query = request.GET.get("term", "")
        companies = TrainedModels.objects.filter(modelTitle__icontains=query)
        results = []
        for company in companies:
            place_json = company.modelTitle
            results.append(place_json)
        data = json.dumps(results)
    mimetype = "application/json"
    return HttpResponse(data, mimetype)

def TrainModelsPage(request):
    return render(request, 'Webapp/TrainModel.html')

@csrf_exempt
def SubmitCSVTrain(request):
    if request.method == 'POST':
        try:
            upload = request.FILES['UploadedFile']

            file_ext = upload.name[-4:]

            if file_ext != '.csv':
                print ('return error')
                data={
                'status' : 'error'
                }
            else:
                #upload file
                user = request.session['userEmail']
                user = user.split('@')
                handle_uploaded_file(upload, user)

                #pre-process file
                dataset = pd.read_csv(settings.BASE_DIR + '/media/temp/' + user[0] + '.csv')
                col = ['Knowledge Base', 'Short Description']
                test1 = dataset[col]
                test1['Knowledge Base']=['__label__'+s.replace(' or ', '$').replace(', or ','$').replace(',','$').replace(' ','_').replace(',','__label__').replace('$$','$').replace('$',' __label__').replace('___','__') for s in test1['Knowledge Base']]
                test1['Knowledge Base']
                test1['Short Description']= test1['Short Description'].replace('\n',' ', regex=True).replace('\t',' ', regex=True)

                REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
                BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
                STOPWORDS = set(stopwords.words('english'))

                def clean_text(text):
                    text = text.lower() # lowercase text
                    text = REPLACE_BY_SPACE_RE.sub(' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text
                    text = BAD_SYMBOLS_RE.sub('', text) # delete symbols which are in BAD_SYMBOLS_RE from text
                    text = ' '.join(word for word in text.split() if word not in STOPWORDS) # delete stopwors from text

                    return text

                test1['Short Description'] = test1['Short Description'].apply(clean_text)

                #store pre-processed data
                test1.to_csv(settings.BASE_DIR + '/media/temp/' + user[0] + 'trainData.txt', index=False, sep=' ', header=False, escapechar=" ", quoting=csv.QUOTE_NONE)

                #get Test Data

                linecount = len(list(open(settings.BASE_DIR + '/media/temp/' + user[0] + 'trainData.txt')))
                splitFile = linecount * 0.3
                splitFile = int(math.floor(splitFile))

                getTestData(splitFile, user[0])
                #finish
                os.remove(settings.BASE_DIR + '/media/temp/' + user[0] + '.csv')
                data={
                'status' : 'success'
                }

        except Exception as e:
            data = {
            'status' : 'error'
            }

    return JsonResponse(data)

def handle_uploaded_file(f, user):
    with open(settings.BASE_DIR + '/media/temp/' + user[0] + '.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def getTestData(fileSplit, user):
    lines = open(settings.BASE_DIR + '/media/temp/' + user + 'trainData.txt').readlines()
    random.shuffle(lines)
    newfile = open(settings.BASE_DIR + '/media/temp/' + user + 'testData.txt', "w")

    for i, line in enumerate(lines):
        if i > fileSplit:
            break
        else:
            newfile.write(line)

def trainModel(request):
    if request.method == 'POST':
        epoch = int(request.POST['epochValue'])
        lr = float(request.POST['learningRateValue'])
        user = request.session['userEmail']
        user = user.split('@')
        """print('epoch:')
        print(epoch)
        print('lr')
        print(lr)"""
        #Train the model
        model = fastText.train_supervised(settings.BASE_DIR + '/media/temp/' + user[0] + 'trainData.txt', lr, epoch)

        #Finished test
        result = model.test(settings.BASE_DIR + '/media/temp/' + user[0] + 'testData.txt')
        precision = float(result[1])
        recall = float(result[2])

        #Compute Accuracy
        Fmeasure = 2 * ((precision *recall) / (precision + recall))
        Fmeasure = "{:.2%}".format(Fmeasure)
        #print('accuracy%')
        #print(Fmeasure)

        #Save model
        model.save_model(settings.BASE_DIR + '/media/temp/' + user[0] + 'trainedModel.bin')

        data = {
        'status' : Fmeasure
        }

    return JsonResponse(data)

def completeModel(request):
    if request.method == 'POST':
        user = request.session['userEmail']
        ModelName = request.POST['modelName']
        ModelDesc = request.POST['modelDesc']

        if UserInfo.objects.filter(email=user).exists():
            if ModelName.isspace() == False and len(ModelName)>=4:
                if ModelDesc.isspace() == False and len(ModelDesc)>=12:
                    if TrainedModels.objects.filter(modelTitle=ModelName).exists():
                        data = {
                        'status' : 'title change'
                        }
                    else:
                        #save model to trainedModel
                        user = user.split("@")
                        path = settings.BASE_DIR + '/media/temp/' + user[0] + 'trainedModel.bin'
                        model = fastText.load_model(path)

                        path = settings.BASE_DIR + '/media/trained/' + ModelName + '.bin'
                        model.save_model(path)

                        os.remove(settings.BASE_DIR + '/media/temp/' + user[0] + 'trainedModel.bin')

                        #success, store to db
                        query = UserInfo.objects.get(email=request.session['userEmail'])

                        TrainedModels.objects.create(email=query, filePath=path, modelTitle=ModelName, modelDescription=ModelDesc)

                        data = {
                        'status' : 'success'
                        }
                else:
                    data = {
                    'status' : 'enter valid description'
                    }
            else:
                data = {
                'status' : 'enter valid model title'
                }
        else:
            data = {
            'status' : 'user not valid'
            }
    return JsonResponse(data)

def predictUsingModel(request):
    try:
        modelName = request.GET['model']
        return render(request, 'Webapp/UseModel.html')
    except:
        return render(request, 'Webapp/404NotFound.html')

@csrf_exempt
def SubmitCSVPredict(request):
    if request.method == 'POST':
        try:
            upload = request.FILES['UploadedFile']
            modelName = request.POST['ModelName']
            file_ext = upload.name[-4:]

            if file_ext != '.csv':
                print ('return error')
                data={
                'status' : 'error'
                }
            else:
                #upload file
                user = request.session['userEmail']
                user = user.split('@')
                handle_uploaded_file(upload, user)

                #pre-process file
                dataset = pd.read_csv(settings.BASE_DIR + '/media/temp/' + user[0] + '.csv')
                col = ['Short Description']
                test1 = dataset[col]
                test1['Short Description']= test1['Short Description'].replace('\n',' ', regex=True).replace('\t',' ', regex=True)

                REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
                BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
                STOPWORDS = set(stopwords.words('english'))

                def clean_text(text):
                    text = text.lower() # lowercase text
                    text = REPLACE_BY_SPACE_RE.sub(' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text
                    text = BAD_SYMBOLS_RE.sub('', text) # delete symbols which are in BAD_SYMBOLS_RE from text
                    text = ' '.join(word for word in text.split() if word not in STOPWORDS) # delete stopwors from text

                    return text

                test1['Short Description'] = test1['Short Description'].apply(clean_text)

                #store pre-processed data
                test1.to_csv(settings.BASE_DIR + '/media/temp/' + user[0] + 'predictData.txt', index=False, sep=' ', header=False, escapechar=" ", quoting=csv.QUOTE_NONE)

                #predict data
                path = settings.BASE_DIR + '/media/trained/' + modelName + '.bin'
                model = fastText.load_model(path)
                predictData = []

                f = open(settings.BASE_DIR + '/media/temp/' + user[0] + 'predictData.txt', "r")
                for x in f:
                    y = x.replace('\n', '')
                    predictData.append(y)

                x = model.predict(predictData)

                print(x)

                data={
                'status' : 'success'
                }

        except Exception as e:
            print(str(e))
            data = {
            'status' : 'error'
            }

    return JsonResponse(data)
