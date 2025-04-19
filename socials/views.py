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
    """
    ViewSet for managing API usage and quotas.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get API Quota Status",
        operation_description="""
        Get current API quota status for all connected platforms.
        
        Returns quota information including:
        - Used requests
        - Limit per platform
        - Reset time
        - Current status (Connected/Limited/Rate Limited)
        
        Rate limits are based on your subscription plan:
        - Free Trial: 100 requests/hour
        - Basic: 1,000 requests/hour
        - Pro: 5,000 requests/hour
        - Enterprise: Unlimited
        """,
        responses={
            200: openapi.Response(
                description="API quota status retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'facebook': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'used': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'limit': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'reset_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['Connected', 'Limited', 'Rate Limited'])
                            }
                        ),
                        'instagram': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'twitter': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'linkedin': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'tiktok': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'telegram': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: 'Authentication credentials not provided',
            403: 'Insufficient subscription plan'
        },
        tags=['API Usage']
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
        operation_summary="Get API Usage Statistics",
        operation_description="""
        Get detailed API usage statistics for a specified time period.
        
        Parameters:
        - period: Time period for statistics (week/month)
        
        Returns daily usage counts per platform.
        """,
        manual_parameters=[
            openapi.Parameter(
                'period',
                openapi.IN_QUERY,
                description="Period for statistics (week/month)",
                type=openapi.TYPE_STRING,
                enum=['week', 'month'],
                required=True
            ),
            openapi.Parameter(
                'platform',
                openapi.IN_QUERY,
                description="Filter by platform",
                type=openapi.TYPE_STRING,
                enum=['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok', 'telegram'],
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="API usage statistics retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'platform': openapi.Schema(type=openapi.TYPE_STRING),
                            'date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                            'count': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            ),
            400: 'Invalid period parameter',
            401: 'Authentication credentials not provided'
        },
        tags=['API Usage']
    )
    def get_usage_stats(self, request):
        """Get API usage statistics"""
        period = request.query_params.get('period', 'week')
        platform = request.query_params.get('platform')
        now = timezone.now()
        
        if period == 'week':
            start_date = now - timedelta(days=7)
        else:  # month
            start_date = now - timedelta(days=30)
            
        query = Q(user=request.user, timestamp__gte=start_date)
        if platform:
            query &= Q(platform=platform)
            
        usage = APIUsageLog.objects.filter(query).values(
            'platform', 'timestamp__date'
        ).annotate(count=models.Count('id')).order_by('timestamp__date')
        
        return Response(usage)

    @staticmethod
    def get_quota_status(quota):
        if quota.used >= quota.limit:
            return 'Rate Limited'
        elif quota.used >= quota.limit * 0.8:  # 80% of limit
            return 'Limited'
        return 'Connected'

class ScheduledPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing scheduled social media posts.
    """
    serializer_class = ScheduledPostSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create Scheduled Post",
        operation_description="""
        Create a new scheduled social media post.
        
        Features:
        - Schedule posts for multiple platforms
        - Upload multiple media files
        - Set custom hashtags per platform
        - Save as draft
        
        Media Limits:
        - Images: Up to 10 images, max 5MB each
        - Videos: Up to 1 video, max 100MB
        - GIFs: Up to 1 GIF, max 15MB
        
        Platform-specific features:
        - Facebook: Multiple images, videos, link previews
        - Instagram: Up to 10 images or 1 video
        - Twitter: Up to 4 images or 1 video
        - LinkedIn: Multiple images, native videos
        - TikTok: Single video
        - Telegram: Multiple media types
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Post content/caption'
                ),
                'hashtags': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Space-separated hashtags'
                ),
                'scheduled_time': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='date-time',
                    description='When to publish the post'
                ),
                'is_draft': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Save as draft without scheduling'
                ),
                'platforms': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'facebook': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'instagram': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'twitter': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'linkedin': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'tiktok': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'telegram': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                ),
                'media': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'file': openapi.Schema(type=openapi.TYPE_FILE),
                            'type': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                enum=['image', 'video', 'gif']
                            ),
                            'alt_text': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            }
        ),
        responses={
            201: ScheduledPostSerializer,
            400: 'Invalid request data',
            401: 'Authentication credentials not provided',
            402: 'Subscription plan limit reached',
            413: 'Media file too large'
        },
        tags=['Scheduled Posts']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List Scheduled Posts",
        operation_description="""
        Get a list of all scheduled posts.
        
        Features:
        - Filter by status (draft/scheduled/published)
        - Filter by platform
        - Filter by date range
        - Sort by scheduled time
        - Pagination
        """,
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by post status",
                type=openapi.TYPE_STRING,
                enum=['draft', 'scheduled', 'published', 'failed'],
                required=False
            ),
            openapi.Parameter(
                'platform',
                openapi.IN_QUERY,
                description="Filter by platform",
                type=openapi.TYPE_STRING,
                enum=['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok', 'telegram'],
                required=False
            ),
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Filter by start date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date',
                required=False
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="Filter by end date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date',
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="List of scheduled posts",
                schema=ScheduledPostSerializer(many=True)
            ),
            401: 'Authentication credentials not provided'
        },
        tags=['Scheduled Posts']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = ScheduledPost.objects.filter(user=self.request.user)
        
        # Apply filters
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(platforms__contains=[platform])
            
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(scheduled_time__date__gte=start_date)
            
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(scheduled_time__date__lte=end_date)
            
        return queryset.order_by('scheduled_time')



   

