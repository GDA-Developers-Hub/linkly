from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from .models import (
    Campaign, AdGroup, Ad, PerformanceReport, 
    KeywordMetrics, GoogleAdsAccount
)
from .serializers import (
    CampaignSerializer, CampaignDetailSerializer,
    AdGroupSerializer, AdGroupDetailSerializer,
    AdSerializer, PerformanceReportSerializer,
    KeywordMetricsSerializer, GoogleAdsAccountSerializer
)
from .services import GoogleAdsService
from .permissions import IsGoogleAdsManager, ReadOnlyUnlessManager

SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.email'
]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def initiate_google_oauth(request):
    """
    Initiates the Google OAuth flow for Google Ads API access
    """
    flow = Flow.from_client_config(
        settings.GOOGLE_OAUTH2_CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=request.build_absolute_uri(reverse('google-oauth-callback'))
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['google_oauth_state'] = state
    return Response({'authorization_url': authorization_url})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_oauth_callback(request):
    """
    Handles the Google OAuth callback and stores the credentials
    """
    state = request.session.get('google_oauth_state')
    flow = Flow.from_client_config(
        settings.GOOGLE_OAUTH2_CLIENT_CONFIG,
        scopes=SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(reverse('google-oauth-callback'))
    )
    
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    # Save or update the Google Ads account
    google_ads_account, created = GoogleAdsAccount.objects.update_or_create(
        user=request.user,
        defaults={
            'refresh_token': credentials.refresh_token,
            'access_token': credentials.token,
            'token_expiry': credentials.expiry,
        }
    )

    return redirect(settings.FRONTEND_URL + '/dashboard/google-ads')

class GoogleAdsAccountViewSet(viewsets.ModelViewSet):
    serializer_class = GoogleAdsAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GoogleAdsAccount.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        """
        Refreshes the access token using the stored refresh token
        """
        try:
            account = self.get_queryset().first()
            if not account:
                return Response(
                    {'error': 'No Google Ads account found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            credentials = Credentials(
                token=account.access_token,
                refresh_token=account.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_OAUTH2_CLIENT_CONFIG['web']['client_id'],
                client_secret=settings.GOOGLE_OAUTH2_CLIENT_CONFIG['web']['client_secret'],
                scopes=SCOPES
            )

            if credentials.expired:
                credentials.refresh(Request())
                account.access_token = credentials.token
                account.token_expiry = credentials.expiry
                account.save()

            return Response(GoogleAdsAccountSerializer(account).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    google_ads_service = GoogleAdsService()
    permission_classes = [ReadOnlyUnlessManager]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CampaignDetailSerializer
        return CampaignSerializer

    def get_queryset(self):
        """Filter campaigns based on user permissions"""
        queryset = Campaign.objects.all()
        if not self.request.user.groups.filter(name='google_ads_managers').exists():
            queryset = queryset.filter(status='ENABLED')
        return queryset

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        campaign = self.get_object()
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        performance_data = PerformanceReport.objects.filter(
            campaign=campaign,
            date__gte=start_date
        ).order_by('date')
        
        serializer = PerformanceReportSerializer(performance_data, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Only managers can sync campaigns"""
        if not request.user.groups.filter(name='google_ads_managers').exists():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        campaign = self.get_object()
        try:
            updated_data = self.google_ads_service.sync_campaign(campaign.id)
            return Response(updated_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdGroupViewSet(viewsets.ModelViewSet):
    queryset = AdGroup.objects.all()
    serializer_class = AdGroupSerializer
    permission_classes = [ReadOnlyUnlessManager]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AdGroupDetailSerializer
        return AdGroupSerializer

    def get_queryset(self):
        """Filter ad groups based on user permissions"""
        queryset = AdGroup.objects.all()
        if not self.request.user.groups.filter(name='google_ads_managers').exists():
            queryset = queryset.filter(status='ENABLED')
        return queryset

    @action(detail=True, methods=['get'])
    def keywords(self, request, pk=None):
        ad_group = self.get_object()
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        keyword_data = KeywordMetrics.objects.filter(
            ad_group=ad_group,
            date__gte=start_date
        ).order_by('-impressions')
        
        serializer = KeywordMetricsSerializer(keyword_data, many=True)
        return Response(serializer.data)

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [ReadOnlyUnlessManager]

    def get_queryset(self):
        """Filter ads based on user permissions"""
        queryset = Ad.objects.all()
        if not self.request.user.groups.filter(name='google_ads_managers').exists():
            queryset = queryset.filter(status='ENABLED')
        return queryset

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Only managers can toggle ad status"""
        if not request.user.groups.filter(name='google_ads_managers').exists():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        ad = self.get_object()
        new_status = request.data.get('status')
        if new_status in ['ENABLED', 'PAUSED', 'REMOVED']:
            ad.status = new_status
            ad.save()
            return Response(AdSerializer(ad).data)
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )

class PerformanceReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PerformanceReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        queryset = PerformanceReport.objects.filter(date__gte=start_date)
        
        # Filter by enabled campaigns for non-managers
        if not self.request.user.groups.filter(name='google_ads_managers').exists():
            queryset = queryset.filter(campaign__status='ENABLED')
        
        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        queryset = PerformanceReport.objects.filter(date__gte=start_date)
        if not request.user.groups.filter(name='google_ads_managers').exists():
            queryset = queryset.filter(campaign__status='ENABLED')
        
        summary = queryset.aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_cost=Sum('cost'),
            total_conversions=Sum('conversions')
        )
        
        return Response(summary)

class KeywordMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = KeywordMetricsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        queryset = KeywordMetrics.objects.filter(date__gte=start_date)
        
        # Filter by enabled ad groups for non-managers
        if not self.request.user.groups.filter(name='google_ads_managers').exists():
            queryset = queryset.filter(ad_group__status='ENABLED')
        
        return queryset 