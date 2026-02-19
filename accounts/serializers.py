from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile
from django.utils import timezone

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('name', 'phone', 'date_of_birth')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'name', 'phone', 'date_of_birth')
    
    def create(self, validated_data):
        name = validated_data.pop('name')
        phone = validated_data.pop('phone')
        date_of_birth = validated_data.pop('date_of_birth', None)
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(
            user=user, 
            name=name, 
            phone=phone,
            date_of_birth=date_of_birth
        )
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name')
    phone = serializers.CharField(source='profile.phone')
    date_of_birth = serializers.DateField(source='profile.date_of_birth', allow_null=True)
    registration_date = serializers.DateTimeField(source='profile.registration_date', read_only=True)
    last_login = serializers.DateTimeField(source='profile.last_login', read_only=True, allow_null=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'phone', 'date_of_birth', 'registration_date', 'last_login')

class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Update last login
        profile = self.user.profile
        profile.last_login = timezone.now()
        profile.save()
        
        # Add user details to response
        user_serializer = UserDetailSerializer(self.user)
        data['user'] = user_serializer.data
        
        return data