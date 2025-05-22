from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_content, name='generate_content'),
    path('optimal-time/', views.get_optimal_time, name='get_optimal_time'),
] 