from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login),
    path('register/', views.register),
    path('forget_password/', views.forget_password),
    path('space/', views.space),
    path('register/submit/', views.reg_sub),
    path('forget_password/submit/', views.for_sub),
    path('login/submit/', views.log_sub),
    path('set_avatar/', views.set_avatar),
    path('set_nickname/', views.set_nickname),
    path('sendcode/submit/', views.sendmsgcode),
    path('logout/', views.logout),
    path('reset_password/', views.reset_password),
    path('more_comments/', views.more_comments),
]