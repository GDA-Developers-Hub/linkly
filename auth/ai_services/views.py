from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from django.conf import settings
from datetime import datetime
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def create_system_prompt(generation_type, context):
    # Base prompt
    prompt = "You are an expert social media content creator."

    # Add platform context
    platforms = context.get('platforms', [])
    if platforms:
        prompt += f"\nOptimizing for: {', '.join(platforms)}"
        for platform in platforms:
            prompt += f"\n- {platform.upper()}: Follow character limits and best practices"

    # Add media context
    media_types = context.get('mediaTypes', [])
    if media_types:
        prompt += f"\n\nContent includes: {', '.join(media_types)}"
        prompt += "\nCreate content that:"
        prompt += "\n- References the media naturally"
        prompt += "\n- Creates a cohesive narrative"

    # Add time context
    scheduled_time = context.get('scheduledTime')
    if scheduled_time:
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            day_of_week = scheduled_dt.strftime('%A')
            hour = scheduled_dt.hour
            
            time_of_day = 'morning' if 5 <= hour < 12 else 'afternoon' if 12 <= hour < 17 else 'evening'
            
            prompt += f"\n\nPost scheduled for {day_of_week} {time_of_day}."
            prompt += f"\nOptimize for {time_of_day} audience engagement"
        except:
            pass

    # Add type-specific instructions
    if generation_type == "caption":
        prompt += "\n\nGenerate an engaging caption that:"
        prompt += "\n- Is authentic and conversational"
        prompt += "\n- Drives user interaction"
        prompt += "\n- Creates emotional connection"
    elif generation_type == "hashtags":
        prompt += "\n\nGenerate strategic hashtags that:"
        prompt += "\n- Mix popular and niche tags"
        prompt += "\n- Are highly relevant"
        prompt += "\n- Maximize discovery potential"

    # Add content structure requirements
    content_structure = context.get('contentStructure', {})
    if content_structure:
        prompt += "\n\nFollow these content requirements:"
        for key, value in content_structure.items():
            prompt += f"\n- {key}: {value}"

    return prompt

@api_view(['POST'])
def generate_content(request):
    try:
        # Extract request data
        generation_type = request.data.get('type')
        prompt = request.data.get('prompt', '')
        context = request.data.get('context', {})

        if not generation_type:
            return Response(
                {'error': 'Missing generation type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create system prompt
        system_prompt = create_system_prompt(generation_type, context)

        # Call OpenAI API with new format
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt or "Generate engaging social media content"}
            ],
            temperature=0.7,
            max_tokens=150
        )

        return Response({
            'content': completion.choices[0].message.content
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def get_optimal_time(request):
    try:
        platform = request.data.get('platform')
        timezone = request.data.get('timezone')

        if not platform or not timezone:
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        system_prompt = f"""You are a social media timing expert. Suggest the best posting time for {platform} in {timezone} timezone.
Consider:
- Peak user activity periods
- Target audience behavior
- Platform-specific algorithms
- Day of the week variations
Return a JSON object with suggested times and brief explanations."""

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"What are the best posting times for {platform} in {timezone}?"}
            ],
            temperature=0.7,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        return Response(json.loads(completion.choices[0].message.content))

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 