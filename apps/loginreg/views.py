from __future__ import unicode_literals
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import User
import bcrypt
import re


def index(request):
    return render(request, "loginreg/index.html")


def successpage(request):
    
    if request.session["login_status_and_id"]["status"]:
        context = {
            "first_name" : User.objects.get(id=request.session["login_status_and_id"]["login_id"]).first_name,
            "last_name" : User.objects.get(id=request.session["login_status_and_id"]["login_id"]).last_name,
        }
        return render(request, "loginreg/successpage.html", context)

    else:
        messages.error(request, "Login error", extra_tags = "login_error")
        redirect("/")


def registrationprocess(request):

    errors = User.objects.custom_registration_validator(request.POST)

    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags = key)
        return redirect("/")

   
    elif len(User.objects.filter(email=request.POST["email"])) > 0:
        errors["duplicated_email_error"] = "Email already exists"
        messages.error(request, errors["duplicated_email_error"], extra_tags = "duplicated_email_error")
        return redirect("/")

    else:
        user_hashpw = bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt())
        User.objects.create(first_name = request.POST["first_name"], last_name = request.POST["last_name"], email = request.POST["email"], password = user_hashpw)
    
     
        request.session["login_status_and_id"] = { "status": True, "login_id": User.objects.get(email=request.POST["email"]).id }
        
        messages.success(request, "Congratulations, you are now an offical member", extra_tags = "registration_success")
        return redirect("/success")

def loginprocess(request):
    
    if len(request.POST["login_password"]) < 1:
        messages.error(request, "Enter your password", extra_tags = "login_pass_error")
 
    if len(request.POST["login_email"]) < 1:
        messages.error(request, "Enter your email address", extra_tags = "login_error")
        return redirect("/")
   
    elif not re.compile(r'^[a-zA-Z0-9+-_]+@[a-zA-Z0-9+-_]+.[a-zA-Z0-9+-_]$').match(request.POST["login_email"]):
        messages.error(request, "Please enter vaild email address (eg. abc123@gmail.com)", extra_tags = "login_error")
        return redirect("/")
   
    elif len(User.objects.filter(email=request.POST["login_email"])) < 1:
        messages.error(request, "that Email address is not in our system", extra_tags = "login_error")
        return redirect("/")
    
    else:
        
        if not bcrypt.checkpw(request.POST["login_password"].encode(), User.objects.get(email=request.POST["login_email"]).password.encode()):
            messages.error(request, "invalid password, please verify and try again", extra_tags = "login_error")
            return redirect("/")
       
        else:
            messages.success(request, "Welcome Back, you are now logged in!", extra_tags = "login_success")
            request.session["login_status_and_id"] = { "status" : True, "login_id" : User.objects.get(email=request.POST["login_email"]).id }
            return redirect("/success")

def logoutprocess(request):
    del request.session["login_status_and_id"]
    return redirect("/")
