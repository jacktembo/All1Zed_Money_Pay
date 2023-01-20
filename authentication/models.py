from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import timezone


class User(AbstractUser):
    user_role = models.CharField(max_length=20, default='user')
    nrc_number = models.CharField(max_length=100, blank=True)
    is_msidn_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15,)
    status = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name']

    def __str__(self):
        return f'{self.username}'


class LimitedCompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="limited")
    account_type = models.CharField(max_length=20, default="limited_company", blank=True)
    is_approved = models.BooleanField(default=False)
    business_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=200, blank=True)
    emai_address = models.EmailField(max_length=100, blank=True)
    organization_type = models.CharField(max_length=200, blank=True)
    tpin_number = models.CharField(max_length=100, blank=True)
    contact_phone_number = models.CharField(max_length=16, blank=True)
    merchant_code = models.CharField(unique=True, max_length=100, blank=True)
    email_address = models.EmailField(max_length=100, blank=True, unique=True)
    pacra_number = models.CharField(max_length=100, blank=True)
    physical_address = models.CharField(max_length=250, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

    # Director 1

    first_director = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='first_director', null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    nrc_number = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=100, blank=True)
    physical_address1 = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)

    # Director 2
    second_director = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='second_director', null=True, blank=True)
    first_name2 = models.CharField(max_length=100, blank=True)
    last_name2 = models.CharField(max_length=100, blank=True)
    nrc_number2 = models.CharField(max_length=100, blank=True)
    email2 = models.EmailField(max_length=100, blank=True)

    # set the first director by default to the user on save

    def set_director(self):
        self.first_director = self.user

    def save(self, *args, **kwargs):
        self.set_director()
        return super(LimitedCompanyProfile, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.business_name)


class OrganizationProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organization")
    account_type = models.CharField(max_length=20, default="organization")
    is_approved = models.BooleanField(default=False)
    business_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=200, blank=True)
    organization_type = models.CharField(max_length=200, blank=True)
    tpin_number = models.CharField(max_length=100, blank=True)
    contact_phone_number = models.CharField(max_length=16, blank=True)
    merchant_code = models.CharField(unique=True, max_length=100, blank=True)
    email_address = models.EmailField(max_length=100, blank=True, unique=True)
    physical_address = models.CharField(max_length=250, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return f"{self.business_name}({self.account_type} Account)"


class BusinessProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    business_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=200, blank=True)
    email_address = models.EmailField(max_length=100, blank=True)
    tpin_number = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    merchant_code = models.CharField(max_length=15, unique=True)
    business_registration_number = models.CharField(max_length=100, blank=True)
    pacra_number = models.CharField(max_length=100, blank=True)
    business_physical_address = models.CharField(max_length=255, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # Director
    director = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_director', null=True, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    physical_address = models.CharField(max_length=100, blank=True)
    nrc_number = models.CharField(max_length=100, blank=True)
    dir_email = models.EmailField(max_length=100, blank=True)

    # Setting the director by default
    def set_director(self):
        self.director = self.user

    def save(self, *args, **kwargs):
        return super(BusinessProfile, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.business_name)


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

    def __str__(self):
        return str(f'business_type: {self.business_type} | branch_name: {self.branch_name}')
