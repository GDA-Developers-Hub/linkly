from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Q
from .models import Post, PostPlatform, PostMedia, PostMetrics
from .serializers import (
    PostSerializer, 
    PostMediaSerializer, 
    SchedulePostSerializer,
    PostMetricsSerializer
)
from .tasks import publish_post_task
import logging

logger = logging.getLogger(__name__)


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Post.objects.filter(user=self.request.user)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by platform if provided
        platform_filter = self.request.query_params.get('platform')
        if platform_filter:
            queryset = queryset.filter(platforms__platform__api_name=platform_filter)
        
        # Search by content
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(content__icontains=search)
        
        # Date range filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class PostMediaView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            post = Post.objects.get(id=pk, user=request.user)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Handle file upload
        file_serializer = PostMediaSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save(post=post)
            return Response(
                file_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        media_id = request.query_params.get('media_id')
        if not media_id:
            return Response(
                {"error": "media_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            media = PostMedia.objects.get(id=media_id, post__id=pk, post__user=request.user)
            media.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PostMedia.DoesNotExist:
            return Response(
                {"error": "Media not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class SchedulePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            post = Post.objects.get(id=pk, user=request.user)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SchedulePostSerializer(data=request.data)
        if serializer.is_valid():
            # Update post status and scheduled time
            post.status = 'scheduled'
            post.scheduled_time = serializer.validated_data['scheduled_time']
            post.save()
            
            # Return updated post
            return Response(
                PostSerializer(post, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublishPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            post = Post.objects.get(id=pk, user=request.user)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the PostPlatform entries for this post
        post_platforms = PostPlatform.objects.filter(post=post)
        
        if not post_platforms.exists():
            return Response(
                {"error": "No platforms found for this post."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the associated SocialAccount instances
        social_accounts = [pp.social_account for pp in post_platforms if pp.social_account]
        
        if not social_accounts:
            return Response(
                {"error": "No social accounts found for this post."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update post status to published
        post.status = 'published'
        post.save()
        
        # Create social account IDs list for the task
        social_account_ids = [social.id for social in social_accounts]
        
        # Update PostPlatform entries
        for pp in post_platforms:
            pp.status = 'scheduled'
            pp.published_at = timezone.now()
            pp.save()
        
        # Trigger the async task with post ID and social account IDs
        publish_post_task.delay(post.id, social_account_ids)

        return Response(
            PostSerializer(post, context={'request': request}).data,
            status=status.HTTP_200_OK
        )


class CancelPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            post = Post.objects.get(
                id=pk, 
                user=request.user,
                status='scheduled'
            )
        except Post.DoesNotExist:
            return Response(
                {"error": "Scheduled post not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update post status back to draft
        post.status = 'draft'
        post.scheduled_time = None
        post.save()
        
        return Response(
            PostSerializer(post, context={'request': request}).data,
            status=status.HTTP_200_OK
        )


class PostMetricsListView(generics.ListAPIView):
    serializer_class = PostMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PostMetrics.objects.filter(
            post__user=self.request.user
        ).select_related('post', 'platform_post', 'platform_post__platform_account')
