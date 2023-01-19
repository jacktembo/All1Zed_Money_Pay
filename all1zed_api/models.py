from django.utils import timezone
# from django.contrib.postgres.fields import JSONField
from authentication.models import User
from django.db import models
from django.conf import settings
from authentication.models import BusinessProfile
import random


class CardAccount(models.Model):
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=16)
    card_number = models.CharField(max_length=200, null=True, blank=True)
    card_id = models.CharField(max_length=200, null=True, blank=True)
    card_balance = models.FloatField(max_length=250, default=0)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def card_ID_generator(self):
        return random.randrange(000000000000000, 999999999999999)


    def __str__(self):
        return str(f'First name: {self.first_name} | Last name: {self.last_name}') 


class BusinessAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    bank_account_number = models.CharField(max_length=200, blank=True)
    account_type = models.CharField(max_length=100)# momo or bank
    commission = models.CharField(max_length=10, default='') #Used on card tap
    merchant_code = models.CharField(max_length=16, unique=True)
    phone_number = models.CharField(max_length=16)
    balance = models.FloatField(max_length=250, default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f'Business name: {self.business_name} | Balance: {self.balance}')
    

class Payment(models.Model):
    service_provider = models.CharField(max_length=200, null=True, blank=True) # mtn, airtel, kazang, zesco, liquid
    service = models.CharField(max_length=200, null=True, blank=True)  # TV, Water, zesco
    phone_number = models.CharField(max_length=250, default=0)
    txn_amount = models.FloatField(max_length=250, default=0)
    card_number = models.CharField(max_length=250, default=0)
    merchant_code = models.FloatField(max_length=250, default=0)
    txn_charge = models.FloatField(max_length=250, default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id}-{self.service_provider}-{self.service}"


class MerchantCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    merchant_code = models.CharField(max_length=15, unique=True)
    business_name = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Branch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE)
    business_type = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200)
    merchant_code = models.CharField(max_length=16, unique=True)
    branch_phone_number = models.CharField(max_length=16)
    notification_phone_number1 = models.CharField(max_length=16)
    notification_phone_number2 = models.CharField(max_length=16, blank=True, null=True)
    notification_phone_number3 = models.CharField(max_length=16, blank=True, null=True)
    branch_address = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class  Meta: 
        verbose_name_plural  =  "Branches" 

    def __str__(self):
        return str(f'business_type: {self.business_type} | branch_name: {self.branch_name}')


class Transaction(models.Model):
    branch_name = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, null=True, blank=True)
    card_number = models.ForeignKey(CardAccount, on_delete=models.SET_NULL, null=True, blank=True)
    account_type = models.CharField(max_length=100, blank=True, null=True) #Card, MOMO or Bank
    institution_name = models.CharField(max_length=100, blank=True, null=True) #Zanaco, Airtel or MTN
    txn_amount = models.CharField(max_length=1000, blank=True, null=True)
    txn_commission = models.CharField(max_length=100, blank=True, null=True)
    update_amount = models.CharField(max_length=1000, blank=True, null=True)
    reference_id = models.CharField(max_length=200, blank=False)
    message = models.CharField(max_length=1000, blank=True)
    status = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.txn_action} - {self.reference_id}'
    

class BusinessTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, blank=True)
    business_name = models.ForeignKey(BusinessAccount,  on_delete=models.CASCADE, null=True, blank=True)
    branch_name = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, null=True, blank=True)
    card_number = models.ForeignKey(CardAccount, on_delete=models.SET_NULL, null=True, blank=True)
    account_type = models.CharField(max_length=100, blank=True, null=True) #Card, MOMO or Bank
    institution_name = models.CharField(max_length=100, blank=True, null=True) #Zanaco, Airtel or MTN
    txn_amount = models.CharField(max_length=1000, blank=True, null=True)
    txn_commission = models.CharField(max_length=100, blank=True, null=True)
    update_amount = models.CharField(max_length=1000, blank=True, null=True)
    reference_id = models.CharField(max_length=200, blank=False)
    message = models.CharField(max_length=1000, blank=True)
    status = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
   

    class Meta:  
        verbose_name  =  "Transaction" 
        verbose_name_plural  =  "Transactions" 

    def __str__(self):
        return f"{self.username} - {self.trans_action} - {self.refference_id}"
