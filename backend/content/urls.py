from django.urls import path
from . import views

urlpatterns = [
    # Caption endpoints
    path('generate-caption/', views.GenerateCaptionView.as_view(), name='generate-caption'),
    path('saved-captions/', views.CaptionListView.as_view(), name='saved-captions'),
    path('saved-captions/<int:pk>/', views.CaptionDetailView.as_view(), name='caption-detail'),
    
    # Hashtag endpoints
    path('generate-hashtags/', views.GenerateHashtagsView.as_view(), name='generate-hashtags'),
    path('hashtags/trending/', views.TrendingHashtagsView.as_view(), name='trending-hashtags'),
    path('hashtags/related/', views.RelatedHashtagsView.as_view(), name='related-hashtags'),
    path('hashtag-groups/', views.HashtagGroupListView.as_view(), name='hashtag-groups'),
    path('hashtag-groups/<int:pk>/', views.HashtagGroupDetailView.as_view(), name='hashtag-group-detail'),
    path('save-hashtag-group/', views.SaveHashtagGroupView.as_view(), name='save-hashtag-group'),
    path('hashtags/performance/', views.HashtagPerformanceView.as_view(), name='hashtag-performance'),
    path('hashtags/refresh-data/', views.RefreshHashtagDataView.as_view(), name='refresh-hashtag-data'),
    
    # Media endpoints
    path('media/', views.MediaListView.as_view(), name='media-list'),
    path('media/<int:pk>/', views.MediaDetailView.as_view(), name='media-detail'),
]
