from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CampaignViewSet,
    AdGroupViewSet,
    AdViewSet,
    PerformanceReportViewSet,
    KeywordMetricsViewSet,
    GoogleAdsAccountViewSet,
    initiate_google_oauth,
    google_oauth_callback
)

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet)
router.register(r'ad-groups', AdGroupViewSet)
router.register(r'ads', AdViewSet)
router.register(r'performance', PerformanceReportViewSet, basename='performance')
router.register(r'keywords', KeywordMetricsViewSet, basename='keywords')
router.register(r'account', GoogleAdsAccountViewSet, basename='account')

urlpatterns = [
    path('auth/init/', initiate_google_oauth, name='google-oauth-init'),
    path('auth/callback/', google_oauth_callback, name='google-oauth-callback'),
    path('', include(router.urls)),
] 