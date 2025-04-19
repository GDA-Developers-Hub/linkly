# social/views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import APIUsageLog, APIQuota, ScheduledPost, PostMedia
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    ScheduledPostSerializer, APIQuotaSerializer, 
    APIUsageLogSerializer, PostMediaSerializer
)

class APIUsageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current API quota status for all platforms",
        responses={
            200: APIQuotaSerializer(many=True),
            401: 'Authentication credentials not provided'
        }
    )
    def get_quota(self, request):
        """Get current API quota status for all platforms"""
        quotas = APIQuota.objects.filter(user=request.user)
        data = {}
        
        for quota in quotas:
            data[quota.platform] = {
                'used': quota.used,
                'limit': quota.limit,
                'reset_at': quota.reset_at,
                'status': self.get_quota_status(quota)
            }
            
        return Response(data)

    @swagger_auto_schema(
        operation_description="Get API usage statistics",
        manual_parameters=[
            openapi.Parameter(
                'period',
                openapi.IN_QUERY,
                description="Period for statistics (week/month)",
                type=openapi.TYPE_STRING,
                enum=['week', 'month']
            )
        ],
        responses={
            200: APIUsageLogSerializer(many=True),
            401: 'Authentication credentials not provided'
        }
    )
    def get_usage_stats(self, request):
        """Get API usage statistics"""
        period = request.query_params.get('period', 'week')
        now = timezone.now()
        
        if period == 'week':
            start_date = now - timedelta(days=7)
        else:  # month
            start_date = now - timedelta(days=30)
            
        usage = APIUsageLog.objects.filter(
            user=request.user,
            timestamp__gte=start_date
        ).values('platform', 'timestamp__date').annotate(
            count=models.Count('id')
        ).order_by('timestamp__date')
        
        return Response(usage)

    @staticmethod
    def get_quota_status(quota):
        if quota.used >= quota.limit:
            return 'Rate Limited'
        elif quota.used >= quota.limit * 0.8:  # 80% of limit
            return 'Limited'
        return 'Connected'

class ScheduledPostViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledPostSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new scheduled post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING),
                'hashtags': openapi.Schema(type=openapi.TYPE_STRING),
                'scheduled_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                'is_draft': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'platforms': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'instagram': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'facebook': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'twitter': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'linkedin': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                ),
                'media': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_FILE)
                )
            }
        ),
        responses={
            201: ScheduledPostSerializer,
            400: 'Invalid data',
            401: 'Authentication credentials not provided'
        }
    )
    def get_queryset(self):
        return ScheduledPost.objects.filter(user=self.request.user)

    def create(self, request):
        """Create a new post"""
        data = request.data
        post = ScheduledPost.objects.create(
            user=request.user,
            content=data['content'],
            hashtags=data.get('hashtags', ''),
            scheduled_time=data.get('scheduled_time'),
            is_draft=data.get('is_draft', False),
            post_to_instagram=data.get('platforms', {}).get('instagram', False),
            post_to_facebook=data.get('platforms', {}).get('facebook', False),
            post_to_twitter=data.get('platforms', {}).get('twitter', False),
            post_to_linkedin=data.get('platforms', {}).get('linkedin', False),
            status='draft' if data.get('is_draft', False) else 'scheduled'
        )

        # Handle media uploads
        media_files = request.FILES.getlist('media')
        for media_file in media_files:
            PostMedia.objects.create(
                post=post,
                file=media_file,
                media_type='image' if media_file.content_type.startswith('image') else 'video'
            )

        return Response(self.get_serializer(post).data)


    @swagger_auto_schema(
        operation_description="Publish a post immediately",
        responses={
            200: openapi.Response(
                description="Post published successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            429: 'Rate limit exceeded',
            401: 'Authentication credentials not provided'
        }
    )
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a post immediately"""
        post = self.get_object()
        
        # Check API quotas before publishing
        platforms = []
        if post.post_to_instagram:
            platforms.append('instagram')
        if post.post_to_facebook:
            platforms.append('facebook')
        if post.post_to_twitter:
            platforms.append('twitter')
        if post.post_to_linkedin:
            platforms.append('linkedin')
            
        # Check quotas for all platforms
        quotas = APIQuota.objects.filter(
            user=request.user,
            platform__in=platforms
        )
        
        # Check if any platform is rate limited
        rate_limited = []
        for quota in quotas:
            if quota.used >= quota.limit:
                rate_limited.append(quota.platform)
                
        if rate_limited:
            return Response({
                'error': f"Rate limited for platforms: {', '.join(rate_limited)}",
                'rate_limited_platforms': rate_limited
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Implement actual posting logic here
        # This would involve calling the respective social media APIs
        
        return Response({'status': 'Post published successfully'})



   

