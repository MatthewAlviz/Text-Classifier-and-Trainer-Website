from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.
class UserInfo(models.Model):
    email = models.EmailField(max_length=250, primary_key=True)
    password = models.CharField(max_length=20)

class TrainedModels(models.Model):
    email = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    filePath = models.CharField(max_length=100)
    modelTitle = models.CharField(max_length=50)
    modelDescription = models.CharField(max_length=200)
    dateCreated = models.DateTimeField(auto_now=True)

class RegistrationQueue(models.Model):
    email = models.EmailField(max_length=250, unique=True)
    password = models.CharField(max_length=20)
    dateCreated = models.DateTimeField(auto_now=True)

class ChangePassQueue(models.Model):
    ticketNo = models.CharField(max_length=20, unique=True)
    email = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_now=True)
    reqCount = models.IntegerField()
