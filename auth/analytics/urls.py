from django.urls import path
from . import views

urlpatterns = [
    path('metrics/', views.AccountMetricsView.as_view(), name='account-metrics'),
    path('audience/', views.AudienceInsightView.as_view(), name='audience-insights'),
    path('best-times/', views.BestTimeToPostView.as_view(), name='best-times-to-post'),
    path('summary/', views.AccountSummaryView.as_view(), name='account-summary'),
]
