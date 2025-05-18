"""
TikTok OAuth2 URLs for Django Allauth.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.oauth2_login, name="tiktok_login"),
    path('login/callback/', views.oauth2_callback, name="tiktok_callback"),
]
