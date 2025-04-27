from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plan-list'),
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('subscription/cancel/', views.CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoice-list'),
]
