from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocialBuProxyViewSet, SocialBuConnectionCallbackView

router = DefaultRouter()
router.register(r'socialbu', SocialBuProxyViewSet, basename='socialbu')

urlpatterns = [
    path('', include(router.urls)),
    path('socialbu/connection/callback/', SocialBuConnectionCallbackView.as_view(), name='socialbu-connection-callback'),
]
