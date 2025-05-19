from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from django.contrib.auth.models import Group
from allauth.socialaccount.models import SocialAccount, SocialApp

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'phone_number', 'company_name', 'website']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    is_google_ads_manager = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_google_ads_manager', 'last_login', 'profile']
        read_only_fields = ['id', 'date_joined']
    
    def get_is_google_ads_manager(self, obj):
        return obj.groups.filter(name='google_ads_managers').exists()
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Update user data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create profile
        if profile_data and hasattr(instance, 'profile'):
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()
        elif profile_data:
            UserProfile.objects.create(user=instance, **profile_data)
        
        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Get refresh and access tokens
        refresh = self.get_token(self.user)
        
        # Restructure to match registration response format
        # Instead of root level tokens, put them in a 'tokens' object
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # Return user data and tokens in consistent format with registration
        return {
            'user': UserSerializer(self.user).data,
            'tokens': tokens
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class ConnectedAccountSerializer(serializers.ModelSerializer):
    social_account_id = serializers.IntegerField(source="id")
    social_app_id = serializers.SerializerMethodField()

    class Meta:
        model = SocialAccount
        # include all model fields + extras
        fields = "__all__"  # this includes: id, provider, uid, user, last_login, extra_data, etc.
        extra_fields = ["social_account_id", "social_app_id"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add custom field values
        representation["social_account_id"] = instance.id
        representation["social_app_id"] = self.get_social_app_id(instance)
        return representation
    
    def get_social_app_id(self, obj):
        # Try to match with SocialApp (may require better logic if using multiple apps per provider)
        try:
            if obj.provider == "linkedin":
                provider = "openid_connect"
            else:
                provider = obj.provider
            return SocialApp.objects.get(provider=provider).id
        except SocialApp.DoesNotExist:
            return None