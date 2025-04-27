from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .models import Caption, Hashtag, HashtagGroup, Media
from .serializers import (
    CaptionSerializer, 
    HashtagSerializer, 
    HashtagGroupSerializer, 
    MediaSerializer,
    CaptionGenerateSerializer,
    HashtagGenerateSerializer
)
import openai
import logging
import os

logger = logging.getLogger(__name__)
# Set the API key directly on the openai module
openai.api_key = os.environ.get('OPENAI_API_KEY', settings.OPENAI_API_KEY)


class GenerateCaptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = CaptionGenerateSerializer(data=request.data)
        if serializer.is_valid():
            prompt = serializer.validated_data['prompt']
            platform = serializer.validated_data['platform']
            tone = serializer.validated_data['tone']
            include_hashtags = serializer.validated_data['include_hashtags']
            hashtag_count = serializer.validated_data.get('hashtag_count', 5)
            
            try:
                # Create system message based on parameters
                system_content = f"You are a professional social media copywriter. Create a compelling {platform} caption with a {tone} tone."
                if include_hashtags:
                    system_content += f" Include {hashtag_count} relevant hashtags at the end."
                
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": f"Write a caption about: {prompt}"}
                    ],
                    max_tokens=500
                )
                
                caption_text = response.choices[0].message.content
                
                # Create a caption object but don't save it yet
                caption = Caption(
                    user=request.user,
                    text=caption_text,
                    platform=platform,
                    is_saved=False
                )
                
                # Return the caption
                return Response({
                    "caption": CaptionSerializer(caption).data,
                    "tokens_used": response.usage.total_tokens
                })
                
            except Exception as e:
                logger.error(f"Error generating caption: {str(e)}")
                return Response(
                    {"error": "Error generating caption. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CaptionListView(generics.ListCreateAPIView):
    serializer_class = CaptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Caption.objects.filter(user=self.request.user, is_saved=True).order_by('-created_at')


class CaptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CaptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Caption.objects.filter(user=self.request.user)


class GenerateHashtagsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = HashtagGenerateSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            platform = serializer.validated_data['platform']
            count = serializer.validated_data['count']
            
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are a social media hashtag expert. Generate {count} popular and relevant hashtags for {platform}."},
                        {"role": "user", "content": f"Generate hashtags for: {query}"}
                    ],
                    max_tokens=200
                )
                
                hashtag_text = response.choices[0].message.content
                
                # Extract hashtags from the text
                import re
                hashtags = re.findall(r'#[\w]+', hashtag_text)
                hashtags = [tag.strip() for tag in hashtags][:count]
                
                # Create or fetch hashtag objects
                hashtag_objects = []
                for tag_name in hashtags:
                    # Remove # from hashtag name
                    clean_name = tag_name[1:] if tag_name.startswith('#') else tag_name
                    hashtag, created = Hashtag.objects.get_or_create(name=clean_name)
                    hashtag_objects.append(hashtag)
                
                return Response({
                    "hashtags": HashtagSerializer(hashtag_objects, many=True).data,
                    "tokens_used": response.usage.total_tokens
                })
                
            except Exception as e:
                logger.error(f"Error generating hashtags: {str(e)}")
                return Response(
                    {"error": "Error generating hashtags. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrendingHashtagsView(generics.ListAPIView):
    serializer_class = HashtagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        platform = self.request.query_params.get('platform', 'instagram')
        return Hashtag.objects.filter(is_trending=True).order_by('-post_count')[:30]


class RelatedHashtagsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        hashtag = request.query_params.get('hashtag', '')
        platform = request.query_params.get('platform', 'instagram')
        
        if not hashtag:
            return Response(
                {"error": "Hashtag parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Find related hashtags using OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are a social media hashtag expert. Given a hashtag, provide 10 related and popular hashtags for {platform} without descriptions. Only return the hashtags, one per line."},
                    {"role": "user", "content": f"Generate related hashtags for: #{hashtag}"}
                ],
                max_tokens=200
            )
            
            hashtag_text = response.choices[0].message.content
            
            # Extract hashtags from the text
            import re
            hashtags = re.findall(r'#?[\w]+', hashtag_text)
            hashtags = [tag.strip('#') for tag in hashtags if tag.strip()][:10]
            
            # Create or fetch hashtag objects
            hashtag_objects = []
            for tag_name in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(name=tag_name)
                hashtag_objects.append(hashtag)
            
            return Response(HashtagSerializer(hashtag_objects, many=True).data)
            
        except Exception as e:
            logger.error(f"Error finding related hashtags: {str(e)}")
            return Response(
                {"error": "Error finding related hashtags. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HashtagGroupListView(generics.ListCreateAPIView):
    serializer_class = HashtagGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HashtagGroup.objects.filter(user=self.request.user).order_by('-created_at')


class HashtagGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HashtagGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HashtagGroup.objects.filter(user=self.request.user)


class MediaListView(generics.ListCreateAPIView):
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Media.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Media.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
