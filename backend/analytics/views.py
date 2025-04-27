from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import AccountMetrics, AudienceInsight, BestTimeToPost
from .serializers import AccountMetricsSerializer, AudienceInsightSerializer, BestTimeToPostSerializer
from platforms.models import PlatformAccount
from posts.models import Post, PostMetrics


class AccountMetricsView(generics.ListAPIView):
    serializer_class = AccountMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AccountMetrics.objects.filter(
            platform_account__user=self.request.user
        ).select_related('platform_account')
        
        # Filter by platform account if provided
        platform_account_id = self.request.query_params.get('platform_account_id')
        if platform_account_id:
            queryset = queryset.filter(platform_account_id=platform_account_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')


class AudienceInsightView(generics.ListAPIView):
    serializer_class = AudienceInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AudienceInsight.objects.filter(
            platform_account__user=self.request.user
        ).select_related('platform_account')
        
        # Filter by platform account if provided
        platform_account_id = self.request.query_params.get('platform_account_id')
        if platform_account_id:
            queryset = queryset.filter(platform_account_id=platform_account_id)
        
        # Filter by date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)
        else:
            # Default to latest date
            latest_date = AudienceInsight.objects.filter(
                platform_account__user=self.request.user
            ).values('date').order_by('-date').first()
            
            if latest_date:
                queryset = queryset.filter(date=latest_date['date'])
        
        return queryset


class BestTimeToPostView(generics.ListAPIView):
    serializer_class = BestTimeToPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = BestTimeToPost.objects.filter(
            user=self.request.user
        ).select_related('platform_account')
        
        # Filter by platform account if provided
        platform_account_id = self.request.query_params.get('platform_account_id')
        if platform_account_id:
            queryset = queryset.filter(platform_account_id=platform_account_id)
        
        # Filter by day of week if provided
        day = self.request.query_params.get('day')
        if day:
            queryset = queryset.filter(day_of_week=day)
        
        return queryset.order_by('day_of_week', 'hour')


class AccountSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Get platform accounts for the user
        platform_accounts = PlatformAccount.objects.filter(
            user=request.user,
            status='connected'
        ).select_related('platform')
        
        # Get the date range (default to last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Get posts for date range
        posts = Post.objects.filter(
            user=request.user,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Get account metrics
        metrics = AccountMetrics.objects.filter(
            platform_account__user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate summary stats
        total_posts = posts.count()
        total_followers = sum(m.followers for m in metrics.filter(date=end_date))
        
        # Calculate average engagement across all platforms
        avg_engagement = metrics.aggregate(avg_engagement=Avg('engagement_rate'))['avg_engagement'] or 0
        
        # Build summary data
        summary = {
            'total_accounts': platform_accounts.count(),
            'total_posts': total_posts,
            'total_followers': total_followers,
            'avg_engagement_rate': avg_engagement,
            'platforms': []
        }
        
        # Add platform-specific summary
        for account in platform_accounts:
            platform_posts = posts.filter(platforms=account).count()
            
            # Get latest metrics if available
            latest_metrics = metrics.filter(
                platform_account=account,
                date=end_date
            ).first()
            
            platform_data = {
                'id': account.id,
                'platform': account.platform.name,
                'account_name': account.account_name,
                'posts_count': platform_posts,
                'followers': latest_metrics.followers if latest_metrics else 0,
                'engagement_rate': latest_metrics.engagement_rate if latest_metrics else 0,
            }
            
            summary['platforms'].append(platform_data)
        
        return Response(summary)
