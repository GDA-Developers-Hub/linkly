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
from openai import OpenAI
import os
import logging
from django.db import models

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', settings.OPENAI_API_KEY))
logger = logging.getLogger(__name__)


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
            media_id = serializer.validated_data.get('media_id')

            try:
                # Check if OpenAI API key is configured
                api_key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
                if not api_key:
                    logger.error("OpenAI API key is not configured")
                    return Response(
                        {"error": "OpenAI API key is not configured. Please set the OPENAI_API_KEY in settings or environment variables."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Initialize OpenAI client with the API key to ensure we're using the latest config
                openai_client = OpenAI(api_key=api_key)
                
                # Create system message based on parameters
                system_content = f"You are a professional social media copywriter. Create a compelling {platform} caption with a {tone} tone."
                if include_hashtags:
                    system_content += f" Include {hashtag_count} relevant hashtags at the end."

                # If media_id is provided, fetch the image details
                media_url = None
                if media_id:
                    try:
                        media = Media.objects.get(id=media_id, user=request.user)
                        media_url = request.build_absolute_uri(media.file.url)
                        # Add instruction to analyze the image
                        if prompt:
                            user_content = f"Write a caption about: {prompt}\n\nThis caption will accompany the image at: {media_url}"
                        else:
                            user_content = f"Write a caption for this image: {media_url}"
                    except Media.DoesNotExist:
                        return Response(
                            {"error": "Media not found or does not belong to this user."},
                            status=status.HTTP_404_NOT_FOUND
                        )
                else:
                    if not prompt:
                        return Response(
                            {"error": "Either a prompt or an image is required for caption generation."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    user_content = f"Write a caption about: {prompt}"

                try:
                    response = openai_client.chat.completions.create(model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": user_content}
                    ],
                    max_tokens=500)
                except Exception as openai_error:
                    logger.error(f"OpenAI API error: {str(openai_error)}")
                    error_message = str(openai_error)
                    
                    # Provide more user-friendly error messages for common issues
                    if "api_key" in error_message.lower():
                        error_message = "Invalid OpenAI API key. Please check your API configuration."
                    elif "rate limit" in error_message.lower():
                        error_message = "OpenAI API rate limit exceeded. Please try again later."
                    elif "insufficient_quota" in error_message.lower():
                        error_message = "OpenAI API quota exceeded. Please check your usage limits."
                    
                    return Response(
                        {"error": error_message},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )

                if not response or not hasattr(response, 'choices') or not response.choices:
                    logger.error("OpenAI API returned an empty or invalid response")
                    return Response(
                        {"error": "Failed to generate caption due to an invalid API response."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                caption_text = response.choices[0].message.content

                # Extract hashtags from the caption if they were included
                hashtags = []
                if include_hashtags:
                    # Simple regex to extract hashtags
                    import re
                    hashtags = re.findall(r'#(\w+)', caption_text)
                    
                    # If no hashtags were found with #, try looking for a list of hashtags
                    if not hashtags and "hashtag" in caption_text.lower():
                        # Try to find a list of hashtags that might not have the # symbol
                        potential_tags = re.findall(r'(?:hashtags?:?\s*|tags?:?\s*)([\w\s,]+)(?:\n|$)', caption_text.lower())
                        if potential_tags:
                            # Split the found text by commas or spaces and clean up
                            for tag_text in potential_tags:
                                for tag in re.findall(r'\b(\w+)\b', tag_text):
                                    if tag and tag not in ['hashtags', 'tags', 'and', 'or', 'the', 'for']:
                                        hashtags.append(tag)

                # Create a caption object but don't save it yet
                caption = Caption(
                    user=request.user,
                    text=caption_text,
                    platform=platform,
                    is_saved=False
                )

                # Prepare the response data
                caption_data = CaptionSerializer(caption).data
                caption_data['hashtags'] = hashtags

                # Return the caption with hashtags
                return Response({
                    "caption": caption_data,
                    "tokens_used": response.usage.total_tokens
                })

            except Exception as e:
                logger.error(f"Error generating caption: {str(e)}")
                # Return a more descriptive error message
                error_message = str(e)
                return Response(
                    {"error": f"Error generating caption: {error_message}"},
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
            content_type = serializer.validated_data['content_type']
            popularity_mix = serializer.validated_data['popularity_mix']

            try:
                # Construct a detailed prompt based on the parameters
                system_prompt = f"""You are a social media hashtag expert specializing in {platform}.
Generate {count} relevant hashtags for a {content_type} about: {query}.

The popularity mix should be {popularity_mix}, meaning:
- If 'balanced': Include a mix of popular, moderately popular, and niche hashtags
- If 'trending': Focus on currently trending and highly popular hashtags
- If 'niche': Focus on more specific, less competitive hashtags

For each hashtag:
1. Exclude the # symbol in your response
2. Make sure each hashtag follows {platform}'s best practices
3. Ensure hashtags are relevant to the content and keywords
4. Do not include spaces in hashtags

Return ONLY a JSON array of hashtags, with no additional text or explanations.
"""

                response = client.chat.completions.create(model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Keywords: {query}"}
                ],
                max_tokens=500,
                response_format={"type": "json_object"})

                # Extract JSON from response
                import json
                try:
                    content = response.choices[0].message.content
                    hashtag_data = json.loads(content)

                    # Handle different possible formats returned by OpenAI
                    if isinstance(hashtag_data, dict) and 'hashtags' in hashtag_data:
                        hashtags = hashtag_data['hashtags']
                    elif isinstance(hashtag_data, dict) and any(k.startswith('hashtag') for k in hashtag_data.keys()):
                        # If returning a dict with hashtag1, hashtag2, etc. keys
                        hashtags = list(hashtag_data.values())
                    elif isinstance(hashtag_data, list):
                        hashtags = hashtag_data
                    else:
                        # Fallback to parsing text if JSON structure is unexpected
                        hashtags = [tag.strip() for tag in content.split(',')]

                    # Clean hashtags - remove # if present and strip spaces
                    cleaned_hashtags = []
                    for tag in hashtags:
                        if isinstance(tag, str):
                            tag = tag.strip()
                            if tag.startswith('#'):
                                tag = tag[1:]
                            # Remove trailing numbers (like '0' at the end)
                            tag = tag.rstrip('0123456789')
                            if tag and ' ' not in tag:  # Skip empty tags or tags with spaces
                                cleaned_hashtags.append(tag)

                    # Create or fetch hashtag objects
                    hashtag_objects = []
                    for tag_name in cleaned_hashtags[:count]:  # Ensure we don't exceed requested count
                        hashtag, created = Hashtag.objects.get_or_create(name=tag_name)
                        hashtag_objects.append(hashtag)

                    return Response({
                        "hashtags": HashtagSerializer(hashtag_objects, many=True).data,
                        "tokens_used": response.usage.total_tokens
                    })

                except json.JSONDecodeError:
                    # If JSON parsing fails, fall back to regex extraction
                    import re
                    hashtags = re.findall(r'#?([\w\d]+)', response.choices[0].message.content)
                    hashtags = [tag for tag in hashtags if tag and ' ' not in tag][:count]

                    # Create or fetch hashtag objects
                    hashtag_objects = []
                    for tag_name in hashtags:
                        hashtag, created = Hashtag.objects.get_or_create(name=tag_name)
                        hashtag_objects.append(hashtag)

                    return Response({
                        "hashtags": HashtagSerializer(hashtag_objects, many=True).data,
                        "tokens_used": response.usage.total_tokens
                    })

            except Exception as e:
                logger.error(f"Error generating hashtags: {str(e)}")
                return Response(
                    {"error": f"Error generating hashtags: {str(e)}. Please try again."},
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
            response = client.chat.completions.create(model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a social media hashtag expert. Given a hashtag, provide 10 related and popular hashtags for {platform} without descriptions. Only return the hashtags, one per line."},
                {"role": "user", "content": f"Generate related hashtags for: #{hashtag}"}
            ],
            max_tokens=200)

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


class SaveHashtagGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Save a group of hashtags after generation.
        Expects:
        {
            "name": "Group Name",
            "platform": "instagram",
            "hashtag_ids": [1, 2, 3] or "hashtag_names": ["tag1", "tag2", "tag3"]
        }
        """
        # Validate required fields
        if not request.data.get('name'):
            return Response(
                {"error": "Group name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get hashtags either by IDs or names
        hashtag_ids = request.data.get('hashtag_ids', [])
        hashtag_names = request.data.get('hashtag_names', [])

        if not hashtag_ids and not hashtag_names:
            return Response(
                {"error": "At least one hashtag is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create new hashtag group
            hashtag_group = HashtagGroup.objects.create(
                user=request.user,
                name=request.data.get('name'),
                platform=request.data.get('platform', 'instagram')
            )

            # Add hashtags to group
            if hashtag_ids:
                hashtags = Hashtag.objects.filter(id__in=hashtag_ids)
                hashtag_group.hashtags.add(*hashtags)

            if hashtag_names:
                for name in hashtag_names:
                    if isinstance(name, str) and name.strip():
                        # Clean hashtag name (remove # if present)
                        clean_name = name.strip()
                        if clean_name.startswith('#'):
                            clean_name = clean_name[1:]

                        hashtag, created = Hashtag.objects.get_or_create(name=clean_name)
                        hashtag_group.hashtags.add(hashtag)

            # Return the created group
            return Response(
                HashtagGroupSerializer(hashtag_group).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error saving hashtag group: {str(e)}")
            return Response(
                {"error": f"Error saving hashtag group: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HashtagPerformanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get hashtag performance metrics by category.
        """
        try:
            # Get all hashtags used by this user through their hashtag groups
            user_hashtag_groups = HashtagGroup.objects.filter(user=request.user)
            user_hashtags = Hashtag.objects.filter(groups__in=user_hashtag_groups).distinct()

            if not user_hashtags.exists():
                # If no hashtags, return placeholder data
                return Response({
                    "categories": [],
                    "metrics": []
                })

            # For demonstration, let's categorize hashtags based on engagement rate
            # In a real system, you might have more sophisticated categorization
            categories = []
            metrics = []

            # Simulate hashtag categories - in a real app, these might come from ML classification
            # or actual social media platform engagement data

            # Get top hashtags by engagement
            top_hashtags = user_hashtags.order_by('-engagement_rate')[:5]
            if top_hashtags:
                categories.append("Top Performing")
                metrics.append({
                    "category": "Top Performing",
                    "average_engagement": round(top_hashtags.aggregate(models.Avg('engagement_rate'))['engagement_rate__avg'] or 0, 2),
                    "hashtags": HashtagSerializer(top_hashtags, many=True).data
                })

            # Get trending hashtags
            trending_hashtags = user_hashtags.filter(is_trending=True)[:5]
            if trending_hashtags:
                categories.append("Trending")
                metrics.append({
                    "category": "Trending",
                    "average_engagement": round(trending_hashtags.aggregate(models.Avg('engagement_rate'))['engagement_rate__avg'] or 0, 2),
                    "hashtags": HashtagSerializer(trending_hashtags, many=True).data
                })

            # Get growing hashtags (highest growth rate)
            growing_hashtags = user_hashtags.order_by('-growth_rate')[:5]
            if growing_hashtags:
                categories.append("Growing")
                metrics.append({
                    "category": "Growing",
                    "average_engagement": round(growing_hashtags.aggregate(models.Avg('engagement_rate'))['engagement_rate__avg'] or 0, 2),
                    "hashtags": HashtagSerializer(growing_hashtags, many=True).data
                })

            # Get low performing hashtags
            low_hashtags = user_hashtags.order_by('engagement_rate')[:5]
            if low_hashtags:
                categories.append("Underperforming")
                metrics.append({
                    "category": "Underperforming",
                    "average_engagement": round(low_hashtags.aggregate(models.Avg('engagement_rate'))['engagement_rate__avg'] or 0, 2),
                    "hashtags": HashtagSerializer(low_hashtags, many=True).data
                })

            return Response({
                "categories": categories,
                "metrics": metrics
            })

        except Exception as e:
            logger.error(f"Error getting hashtag performance: {str(e)}")
            return Response(
                {"error": f"Error retrieving hashtag performance data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshHashtagDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Refresh hashtag data by fetching the latest information.
        This simulates getting updated metrics from social media platforms.
        In a production app, this would connect to actual platform APIs.
        """
        platform = request.data.get('platform', 'instagram')

        try:
            # First, get trending hashtags for the selected platform
            # In a real app, this would use the social media platform's API
            # Here we're using OpenAI to simulate this

            response = client.chat.completions.create(model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a social media trend expert for {platform}. Provide a list of 10 currently trending hashtags as a JSON array. Include only hashtag names without the # symbol."},
                {"role": "user", "content": f"What are the current trending hashtags on {platform}?"}
            ],
            max_tokens=300,
            response_format={"type": "json_object"})

            import json
            import random

            try:
                content = response.choices[0].message.content
                data = json.loads(content)

                # Extract hashtags
                trending_hashtags = []
                if isinstance(data, dict) and 'hashtags' in data:
                    trending_hashtags = data['hashtags']
                elif isinstance(data, list):
                    trending_hashtags = data
                else:
                    # Try to extract from any JSON field that might contain the hashtags
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            trending_hashtags = value
                            break

                # If we still don't have hashtags, fallback
                if not trending_hashtags:
                    trending_hashtags = ['fashion', 'travel', 'food', 'fitness', 'photography', 
                                        'art', 'music', 'nature', 'technology', 'business']

                # Clean the hashtags
                trending_hashtags = [tag.strip('#') if isinstance(tag, str) else str(tag) for tag in trending_hashtags]

                # Update or create trending hashtags with simulated metrics
                refreshed_hashtags = []

                for tag_name in trending_hashtags:
                    # Generate realistic metrics
                    post_count = random.randint(10000, 1000000)
                    growth_rate = random.uniform(1.0, 15.0)  # 1% to 15% growth
                    engagement_rate = random.uniform(1.0, 10.0)  # 1% to 10% engagement

                    # Create or update the hashtag
                    hashtag, created = Hashtag.objects.update_or_create(
                        name=tag_name,
                        defaults={
                            'post_count': post_count,
                            'growth_rate': growth_rate,
                            'engagement_rate': engagement_rate,
                            'is_trending': True,
                            'last_updated': models.functions.Now()
                        }
                    )
                    refreshed_hashtags.append(hashtag)

                # Update some existing hashtags to keep the database current
                # In a real app, you would pull actual metrics from social platforms
                existing_hashtags = Hashtag.objects.exclude(name__in=trending_hashtags).order_by('?')[:20]
                for hashtag in existing_hashtags:
                    # Generate realistic updated metrics
                    hashtag.post_count = max(1000, hashtag.post_count + random.randint(-5000, 10000))
                    hashtag.growth_rate = max(0, min(20, hashtag.growth_rate + random.uniform(-2.0, 2.0)))
                    hashtag.engagement_rate = max(0, min(15, hashtag.engagement_rate + random.uniform(-1.0, 1.0)))
                    hashtag.is_trending = random.random() < 0.2  # 20% chance of being trending
                    hashtag.save()
                    refreshed_hashtags.append(hashtag)

                return Response({
                    "message": f"Successfully refreshed hashtag data for {platform}",
                    "refreshed_count": len(refreshed_hashtags),
                    "trending_hashtags": HashtagSerializer(
                        Hashtag.objects.filter(is_trending=True).order_by('-post_count')[:10], 
                        many=True
                    ).data
                })

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from OpenAI: {str(e)}")
                return Response(
                    {"error": "Error processing trending hashtags. Using fallback data."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error refreshing hashtag data: {str(e)}")
            return Response(
                {"error": f"Error refreshing hashtag data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
