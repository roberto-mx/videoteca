from django.shortcuts import render
from django.contrib.auth.views import LoginView    

class AdminLogin(LoginView):
    template_name = 'base.html'
