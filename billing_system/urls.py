"""
URL configuration for billing_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app01 import views
from django.conf.urls import include
from captcha import *
from django.urls import re_path


urlpatterns = [
    path('login/',views.login.as_view()),
    path('register/',views.register.as_view()),
    path('month_budget/',views.month_budgetView.as_view()),
    # path('captcha/', include('captcha.urls')),
    path('getbudget/', views.getbudget.as_view()),
    path('Clock_in/', views.Clock_inView.as_view()),
    path('get_p_information/', views.get_p_informationView.as_view()),
    re_path(r'^get(?P<period>week|month|year)bill/$', views.BillingListView.as_view()),
    re_path(r'^get(?P<period>yearly|monthly)bill/$', views.BillDetailView.as_view()),
    # path('refresh_captcha/', views.refresh_captcha),
    # path('test/',views.IndexView.as_view()),

]
