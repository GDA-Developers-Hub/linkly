from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import qrcode
import base64
from io import BytesIO
from .models import User, Subscription, SubscriptionPlan

User = get_user_model()

# class UserSerializer(serializers.ModelSerializer):
#     """User model serializer."""
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ('id', 'email', 'password', 'first_name', 'last_name', 'is_active')
#         read_only_fields = ('id', 'is_active')

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user

class UserSerializer(serializers.ModelSerializer):
    """User profile serializer."""
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'company_name',
            'website', 'industry', 'phone_number', 'country',
            'profile_picture', 'timezone', 'date_joined'
        )
        read_only_fields = ('id', 'email', 'date_joined')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token obtain pair serializer."""
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class TwoFactorSerializer(serializers.Serializer):
    """2FA serializer."""
    token = serializers.CharField(required=True, min_length=6, max_length=6)

class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer."""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    features = serializers.JSONField(source='plan.features', read_only=True)
    price = serializers.DecimalField(source='plan.price', max_digits=10, decimal_places=2, read_only=True)
    interval = serializers.CharField(source='plan.interval', read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = (
            'id', 'plan_name', 'features', 'price', 'interval',
            'status', 'start_date', 'end_date', 'is_active',
            'is_trial', 'trial_end_date'
        )
        read_only_fields = fields

class SocialAccountSerializer(serializers.ModelSerializer):
    """Social account serializer."""
    class Meta:
        model = User
        fields = (
            'google_id', 'facebook_id', 'twitter_id', 'linkedin_id',
            'instagram_id', 'tiktok_id', 'telegram_id',
            'has_facebook_business', 'has_instagram_business',
            'has_linkedin_company', 'has_twitter_business',
            'has_tiktok_business', 'has_telegram_channel'
        )
        read_only_fields = fields

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
            
        # Ensure username is provided and not automatically set to email
        if 'username' not in attrs or not attrs['username']:
            raise serializers.ValidationError({"username": "Username is required"})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        # Create user with provided username
        user = User.objects.create_user(**validated_data)
        return user

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

    def validate(self, attrs):
        # Implement platform-specific validation
        return attrs

    def create(self, validated_data):
        # Implement platform-specific connection creation
        return validated_data 