from django.contrib import admin
from .models import CardAccount, BusinessAccount
from authentication.models import OrganizationProfile

# Register your models here.

admin.site.register(CardAccount)
admin.site.register(BusinessAccount)


