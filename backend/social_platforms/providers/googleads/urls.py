"""
Google Ads OAuth2 URLs for Django Allauth.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.oauth2_login, name="googleads_login"),
    path('login/callback/', views.oauth2_callback, name="googleads_callback"),
]
