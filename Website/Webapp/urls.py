from django.conf.urls import url, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', views.base, name='base'),
    url(r'^register/$', views.validateRegForm, name='validateRegForm'),
    url(r'^logIn/$', views.logIn, name='logIn'),
    url(r'^logOut/$', views.logOut, name='logOut'),
    url(r'^confirm/$', views.confirmAccount, name='confirmAccount'),
    url(r'^forgotPass/$', views.forgotPass, name='forgotPass'),
    url(r'^keepLogged/$', views.keepLoggedIn, name='keepLoggedIn'),
    url(r'^changePass/$', views.changePass, name='changePass'),
    url(r'^verifyPass/$', views.verifyPass, name='verifyPass'),
    url(r'^searchModels/$', views.searchModelsPage, name='searchModelsPage'),
    url(r'^autocomplete/$', views.models_autocomplete, name='models_autocomplete'),
    url(r'^train/$', views.TrainModelsPage, name='TrainModelsPage'),
    url(r'^submitTrainData/$', views.SubmitCSVTrain, name='SubmitCSVTrain'),
    url(r'^startTrain/$', views.trainModel, name='trainModel'),
    url(r'^completeTrain/$', views.completeModel, name='completeModel'),
    url(r'^useModel/$', views.predictUsingModel, name='predictUsingModel'),
    url(r'^submitPredictData/$', views.SubmitCSVPredict, name='SubmitCSVPredict'),
    url(r'^downloadHere/$', views.downloadHere, name='downloadHere'),
    url(r'^downloadResult/$', views.extractResult, name='extractResult')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
