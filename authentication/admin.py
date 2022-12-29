from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.


from .models import LimitedCompanyProfile, OrganizationProfile, BusinessProfile

admin.site.register(LimitedCompanyProfile)
admin.site.register(OrganizationProfile)
admin.site.register(BusinessProfile)

