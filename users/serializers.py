from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import qrcode
import base64
from io import BytesIO
from .models import User, Subscription, SubscriptionPlan

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    connected_platforms = serializers.SerializerMethodField()
    subscription_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_business', 'company_name', 
                 'phone_number', 'profile_picture', 'instagram_handle', 
                 'twitter_handle', 'linkedin_profile', 'youtube_channel', 
                 'facebook_page', 'tiktok_handle', 'business_description', 
                 'website', 'industry', 'two_factor_enabled', 'connected_platforms', 'subscription_status')
        read_only_fields = ('id', 'two_factor_enabled', 'connected_platforms', 'subscription_status')

    def get_connected_platforms(self, obj):
        platforms = []
        
        # Check each platform
        if obj.facebook_id:
            platforms.append({
                'platform': 'facebook',
                'connected': True,
                'profile_url': obj.facebook_page or '',
                'handle': obj.facebook_page_name or '',
                'followers': obj.facebook_page_followers,
                'is_business': obj.has_facebook_business,
                'last_synced': obj.get_last_sync('facebook')
            })
        
        if obj.instagram_id:
            platforms.append({
                'platform': 'instagram',
                'connected': True,
                'profile_url': obj.instagram_profile_url or '',
                'handle': obj.instagram_handle or '',
                'followers': obj.instagram_business_followers,
                'is_business': obj.has_instagram_business,
                'last_synced': obj.get_last_sync('instagram')
            })
        
        # Add similar blocks for other platforms
        platform_checks = [
            ('twitter', 'twitter_id', 'twitter_profile_url', 'twitter_handle', 'twitter_followers'),
            ('linkedin', 'linkedin_id', 'linkedin_profile', 'linkedin_company_name', 'linkedin_company_followers'),
            ('youtube', 'youtube_id', 'youtube_channel', 'youtube_channel_title', 'youtube_subscribers'),
            ('tiktok', 'tiktok_id', 'tiktok_profile_url', 'tiktok_handle', 'tiktok_followers'),
            ('telegram', 'telegram_id', 'telegram_username', 'telegram_channel_name', 'telegram_subscribers')
        ]
        
        for platform, id_field, url_field, handle_field, followers_field in platform_checks:
            if getattr(obj, id_field):
                platforms.append({
                    'platform': platform,
                    'connected': True,
                    'profile_url': getattr(obj, url_field) or '',
                    'handle': getattr(obj, handle_field) or '',
                    'followers': getattr(obj, followers_field),
                    'is_business': getattr(obj, f'has_{platform}_business', False),
                    'last_synced': obj.get_last_sync(platform)
                })
        
        return platforms

    def get_subscription_status(self, obj):
        if not obj.current_subscription:
            return {
                'status': 'NONE',
                'plan': None,
                'days_remaining': '0',
                'is_trial': False
            }
        
        return {
            'status': obj.current_subscription.status,
            'plan': obj.current_subscription.plan.name,
            'days_remaining': obj.current_subscription.days_remaining(),
            'is_trial': obj.current_subscription.is_trial
        }

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'is_business', 
                 'company_name', 'phone_number')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Check if 2FA is enabled
        if user.two_factor_enabled:
            data['requires_2fa'] = True
            data['user_id'] = user.id
            # Don't include tokens yet
            return data
            
        # If 2FA is not enabled, include user data and tokens
        data['user'] = UserSerializer(user).data
        # Store tokens in user model for Node.js compatibility
        user.update_jwt_tokens(data['access'], data['refresh'])
        return data

class Verify2FASerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(id=attrs['user_id'])
            if not user.verify_2fa(attrs['code']):
                raise serializers.ValidationError({"code": "Invalid 2FA code"})
            attrs['user'] = user
            return attrs
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User not found"})

class Enable2FASerializer(serializers.Serializer):
    qr_code = serializers.SerializerMethodField()
    backup_codes = serializers.ListField(read_only=True)
    secret = serializers.CharField(read_only=True)

    def get_qr_code(self, obj):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(obj.get_2fa_uri())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to base64 string
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'is_business', 'company_name', 
                 'phone_number', 'profile_picture', 'instagram_handle', 
                 'twitter_handle', 'linkedin_profile', 'youtube_channel', 
                 'facebook_page', 'tiktok_handle', 'business_description', 
                 'website', 'industry')
        
    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class SocialConnectionSerializer(serializers.Serializer):
    platform = serializers.CharField()
    auth_code = serializers.CharField()
    redirect_uri = serializers.CharField(required=False)
    business_account = serializers.BooleanField(default=False)

class SocialAccountSerializer(serializers.Serializer):
    platform = serializers.CharField()
    connected = serializers.BooleanField()
    profile_url = serializers.CharField()
    handle = serializers.CharField()
    followers = serializers.IntegerField()
    is_business = serializers.BooleanField()
    last_synced = serializers.CharField() 