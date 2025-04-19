from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import qrcode
import base64
from io import BytesIO

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_business', 'company_name', 
                 'phone_number', 'profile_picture', 'instagram_handle', 
                 'twitter_handle', 'linkedin_profile', 'youtube_channel', 
                 'facebook_page', 'tiktok_handle', 'business_description', 
                 'website', 'industry', 'two_factor_enabled')
        read_only_fields = ('id', 'two_factor_enabled')

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