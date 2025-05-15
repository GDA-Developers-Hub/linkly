"""
YouTube OAuth2 URLs for Django Allauth.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.oauth2_login, name="youtube_login"),
    path('login/callback/', views.oauth2_callback, name="youtube_callback"),
]
