from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.base, name='base'),
    url(r'^register/$', views.validateRegForm, name='validateRegForm'),
    url(r'^logIn/$', views.logIn, name='logIn'),
    url(r'^logOut/$', views.logOut, name='logOut')
]
