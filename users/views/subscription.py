from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from ..serializers import SubscriptionSerializer

class SubscriptionStatusView(generics.RetrieveAPIView):
    """View subscription status."""
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_object(self):
        return self.request.user.current_subscription

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_plans(request):
    """Get available subscription plans."""
    from ..models import SubscriptionPlan
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return Response({
        'plans': [
            {
                'id': plan.id,
                'name': plan.name,
                'price': str(plan.price),
                'interval': plan.interval,
                'features': plan.features,
                'is_popular': plan.is_popular
            }
            for plan in plans
        ]
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """Create a Stripe checkout session."""
    try:
        plan_id = request.data.get('plan')
        from ..models import SubscriptionPlan
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        # Create Stripe checkout session
        session = plan.create_checkout_session(request.user)
        
        return Response({
            'session_id': session.id,
            'public_key': settings.STRIPE_PUBLIC_KEY
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST) 