# coding=utf-8
from django.conf.urls import url

from . import views

__author__ = 'Daniël'

urlpatterns = [
    url(r'^$', views.MainPageView.as_view(), name='mainpage'),
    url(r'^collections$', views.CollectionsView.as_view(), name='collections'),
]
