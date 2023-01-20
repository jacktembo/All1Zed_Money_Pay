from django.contrib import admin
from .models import CardAccount, BusinessAccount, BusinessTransaction
from authentication.models import User, Branch

# Register your models here.

admin.site.register(User)
admin.site.register(CardAccount)
admin.site.register(BusinessAccount)
admin.site.register(BusinessTransaction)
admin.site.register(Branch)


