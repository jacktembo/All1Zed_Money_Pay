from django.contrib import admin
from .models import CardAccount, BusinessAccount, BusinessTransaction, Branch
from authentication.models import OrganizationProfile, User, BusinessProfile

# Register your models here.

admin.site.register(User)
admin.site.register(CardAccount)
admin.site.register(BusinessAccount)
admin.site.register(OrganizationProfile)
admin.site.register(BusinessAccount)
admin.site.register(BusinessTransaction)
admin.site.register(BusinessProfile)
admin.site.register(Branch)


