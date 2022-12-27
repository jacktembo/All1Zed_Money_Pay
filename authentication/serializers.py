from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.fields import CharField
from rest_framework.relations import StringRelatedField
#from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, BusinessProfile, OrganizationProfile
from all1zed_api.models import CardAccount
from .helper_functions import id_generator
import phonenumbers


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(min_length=2, max_length=255)
    last_name = serializers.CharField(min_length=2, max_length=255)
    email = serializers.EmailField(min_length=8, max_length=255)
    username = serializers.CharField(min_length=2, max_length=255)
    password = serializers.CharField(min_length=6, max_length=65, write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

    def validate(self, attrs):
        email = attrs.get('email', None)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'Error': 'Email already in use'})
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class OrganizationProfileSerializer(serializers.ModelSerializer):
    user = StringRelatedField()
    created_by = StringRelatedField()

    class Meta:
        model = OrganizationProfile
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}, 'created_by': {'read_only': True},
                        'merchant_code': {'read_only': True}, "tpin_number": {'required': False},
                        "tpin_file": {'required': False}}


class BusinessProfileSerializer(serializers.ModelSerializer):
    user = StringRelatedField()
    created_by = StringRelatedField()
    tpin_number = serializers.CharField()
    pacra_number = serializers.CharField()

    class Meta:
        model = BusinessProfile
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}, 'created_by': {'read_only': True}, 
                        'merchant_code': {'read_only': True}}
    

class CreateBusinessSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessProfile
        exclude = ('user', 'created_by', 'merchant_code')


class CreateOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationProfile
        exclude = ('user', 'created_by', 'merchant_code')


class CardAccountSerializer(serializers.ModelSerializer):
    card_id = serializers.SerializerMethodField(method_name='render_card_id')
#    credit_card_number = serializers.CharField(max_length=255, source='card_number')

    def render_card_id(self, card):
        return id_generator()

    class Meta:
        model = CardAccount
        fields = ['first_name', 'last_name', 'phone_number', 'card_id', 'card_number']


class BlockCardSerializer(serializers.ModelSerializer):
    class meta:
        model = CardAccount
        fields = ['card_number']    




























