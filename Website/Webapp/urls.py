from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.base, name='base'),
    url(r'^register/$', views.validateRegForm, name='validateRegForm'),
    url(r'^logIn/$', views.logIn, name='logIn'),
    url(r'^logOut/$', views.logOut, name='logOut'),
    url(r'^confirm/$', views.confirmAccount, name='confirmAccount'),
    url(r'^forgotPass/$', views.forgotPass, name='forgotPass'),
    url(r'^keepLogged/$', views.keepLoggedIn, name='keepLoggedIn')
]
