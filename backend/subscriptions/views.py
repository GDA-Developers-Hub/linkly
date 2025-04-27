from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Plan, Subscription, Invoice
from .serializers import PlanSerializer, SubscriptionSerializer, InvoiceSerializer
from django.utils import timezone


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionView(generics.RetrieveAPIView, generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Get the most recent active subscription
        try:
            return Subscription.objects.filter(
                user=self.request.user,
                status__in=['active', 'trial']
            ).latest('created_at')
        except Subscription.DoesNotExist:
            return None
    
    def get(self, request, *args, **kwargs):
        subscription = self.get_object()
        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        return Response({"detail": "No active subscription found."}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        # First cancel any existing subscriptions
        active_subs = Subscription.objects.filter(
            user=request.user,
            status__in=['active', 'trial']
        )
        for sub in active_subs:
            sub.status = 'canceled'
            sub.end_date = timezone.now()
            sub.save()
        
        # Create new subscription
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CancelSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            subscription = Subscription.objects.filter(
                user=request.user,
                status__in=['active', 'trial']
            ).latest('created_at')
            
            subscription.status = 'canceled'
            subscription.end_date = timezone.now()
            subscription.save()
            
            return Response({"detail": "Subscription canceled successfully."}, status=status.HTTP_200_OK)
        except Subscription.DoesNotExist:
            return Response({"detail": "No active subscription found."}, status=status.HTTP_404_NOT_FOUND)


class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Invoice.objects.filter(
            subscription__user=self.request.user
        ).order_by('-invoice_date')
