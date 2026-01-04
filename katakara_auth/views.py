from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import KatakaraUser

# Create your views here.


#signup
#login
#logout
#forgot password
@api_view("POST")
def create_katakarauser(request):
    user = KatakaraUser.objects.create_user()