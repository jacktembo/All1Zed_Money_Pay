from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from all1zed_api.models import (
    CardAccount, BusinessAccount, 
    Transaction, Payment,
)
from authentication.models import BusinessProfile



class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardAccount
        fields = ['card_balance']


class CardsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardAccount
        fields = '__all__'


class BusinessAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAccount
        fields = ['merchant_code', 'business_name']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class CardPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['merchant_code', 'txn_amount', 'card_number']
        

class TotalDebitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['txn_amount']


class BusinessProfileListSerializer(serializers.ModelSerializer):
    created_by = StringRelatedField()

    class Meta:
        model = BusinessProfile
        fields = '__all__'
