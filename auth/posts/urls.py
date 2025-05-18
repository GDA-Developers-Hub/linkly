from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/media/', views.PostMediaView.as_view(), name='post-media'),
    path('<int:pk>/schedule/', views.SchedulePostView.as_view(), name='schedule-post'),
    path('<int:pk>/publish/', views.PublishPostView.as_view(), name='publish-post'),
    path('<int:pk>/cancel/', views.CancelPostView.as_view(), name='cancel-post'),
    path('metrics/', views.PostMetricsListView.as_view(), name='post-metrics'),
]
