from django.contrib import admin
from .models import UserInfo, TrainedModels, RegistrationQueue, ChangePassQueue

# Register your models here.
admin.site.register(UserInfo)
admin.site.register(TrainedModels)
admin.site.register(RegistrationQueue)
admin.site.register(ChangePassQueue)
